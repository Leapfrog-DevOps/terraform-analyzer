import os
import re
import hcl2
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CODE_PATH = os.getenv("CODE_PATH", "./terraform/")


def retrieve_relevant_context(log_content):
    """
    Extract file references from log and retrieve their content directly from repo
    Preserves original code structure completely
    """
    # Extract file references from Terraform errors
    file_patterns = [
        r'on ([\w\-\/\.]+\.tf) line (\d+)',
        r'in ([\w\-\/\.]+\.tf)',
        r'Error.*?([\w\-\/\.]+\.tf)',
        r'module\.([\w\-]+)',
    ]

    referenced_files = set()

    for pattern in file_patterns:
        matches = re.findall(pattern, log_content)
        for match in matches:
            if isinstance(match, tuple):
                referenced_files.add(match[0])
            else:
                referenced_files.add(match)

    # If no specific files found in log, include all .tf files in CODE_PATH
    if not referenced_files:
        for root, _, files in os.walk(CODE_PATH):
            for file in files:
                if file.endswith(".tf"):
                    file_path = os.path.join(root, file)
                    # Make path relative to CODE_PATH for consistency
                    rel_path = os.path.relpath(file_path, CODE_PATH)
                    referenced_files.add(rel_path)

    context = ""
    for file_path in referenced_files:
        # Construct full path from CODE_PATH
        full_path = os.path.join(CODE_PATH, file_path) if not os.path.isabs(file_path) else file_path

        if os.path.exists(full_path):
            try:
                with open(full_path, 'r') as f:
                    content = f.read()
                context += f"\n## File: {file_path}\n```hcl\n{content}\n```\n"
            except Exception as e:
                context += f"\n## File: {file_path}\n[Error reading file: {e}]\n"

    return context


def read_terraform_logs():
    log_path = "logs/terraform.log"
    if not os.path.exists(log_path):
        return "No logs found."
    with open(log_path, "r") as file:
        return file.read()


def get_ai_feedback(log_content, temperature=0):
    """
    Get AI feedback for Terraform errors with complete code blocks
    """
    context = retrieve_relevant_context(log_content)

    prompt = f"""ROLE: You are a Terraform expert. Analyze this failure log systematically and provide solutions to fix in code.

CRITICAL REQUIREMENTS:
- Keep the source code as original as possible to avoid information loss
- NEVER use "# other configurations..." or "..." or any truncation or lazy writing
- Always provide COMPLETE resource blocks with ALL existing attributes EXACTLY as they appear in the original code
- Work with ANY AWS resource type (EC2, S3, RDS, Lambda, SQS, etc.)
- Preserve ALL original attributes, nested blocks, configurations, formatting, and indentation
- Only fix the specific error - keep everything else IDENTICAL to the original
- Copy the entire original block and only change the problematic line(s)

REQUIRED OUTPUT FORMAT (no deviations):

File: [exact_file_path]
Block Name: [block_type] "[block_name]" 
Issue: [one sentence description of the specific error]
Solution:
```hcl
[Write the COMPLETE original resource block with ALL attributes, nested blocks, tags, etc. - only fix the specific error, keep everything else IDENTICAL. No shortcuts, no omissions, no lazy writing like "other configuration etc."]
```

ANALYSIS RULES:
- Analyze errors in the order they appear in the log
- Include COMPLETE resource blocks in solutions (copy original and fix only the error)
- Only output blocks that contain actual errors
- Use exact file paths from the log
- Maintain ALL original attributes, tags, lifecycle blocks, comments, formatting
- Separate multiple issues with a blank line
- Show the ENTIRE block exactly as it appears in original code, not just changed parts
- Preserve original indentation, spacing, and code style

LOG TO ANALYZE:
{log_content}

TERRAFORM FILES (ORIGINAL SOURCE CODE):
{context}

Begin systematic analysis - copy original blocks completely and fix only the specific errors:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system",
                 "content": "You are a Terraform and AWS expert. Always preserve original code structure and provide complete blocks."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"


def extract_code_fixes(ai_response):
    pattern = r"File:\s*(.*?)\nBlock Name:\s*(.*?)\n.*?```hcl(.*?)```"

    matches = re.findall(pattern, ai_response, re.DOTALL)
    fixes = []
    for match in matches:
        file_path, block_name, corrected_code = match
        fixes.append({
            "file": file_path.strip(),
            "block_name": block_name.strip(),
            "suggestion": corrected_code.strip()
        })
    return fixes


def parse_block_name(block_name_str):
    parts = re.findall(r'"(.*?)"', block_name_str)
    block_type = block_name_str.split()[0]  # module, resource, etc.

    if len(parts) == 1:
        return block_type, parts[0], None
    elif len(parts) == 2:
        return block_type, parts[0], parts[1]
    else:
        return block_type, None, None


def find_block_lines(file_path, block_type, name1=None, name2=None):
    start_line = None
    end_line = None
    open_braces = 0
    in_block = False

    with open(file_path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        stripped = line.strip()

        if name1 and name2:
            expected_start = f'{block_type} "{name1}" "{name2}"'
        elif name1:
            expected_start = f'{block_type} "{name1}"'
        else:
            expected_start = block_type

        if not in_block and stripped.startswith(expected_start) and stripped.endswith('{'):
            start_line = i
            open_braces = 1
            in_block = True
            continue

        if in_block:
            open_braces += line.count('{')
            open_braces -= line.count('}')
            if open_braces == 0:
                end_line = i
                break

    if start_line is not None and end_line is not None:
        return start_line + 1, end_line + 1
    else:
        return None, None


def apply_fixes_to_file(fix):
    file_path = os.path.join(CODE_PATH, fix["file"])
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False

    try:
        with open(file_path, "r") as f:
            lines = f.readlines()

        block_type, name1, name2 = parse_block_name(fix['block_name'])
        start_line, end_line = find_block_lines(file_path, block_type, name1, name2)

        if start_line is None or end_line is None:
            print(f"Error: Could not find block {fix['block_name']} in {file_path}")
            return False

        suggestion_lines = fix["suggestion"].strip().splitlines()
        suggestion_block = [f"{line}\n" for line in suggestion_lines]

        # Backup original content
        backup_path = f"{file_path}.backup"
        with open(backup_path, "w") as f:
            f.writelines(lines)
        print(f"Created backup: {backup_path}")

        # Apply fix
        lines[start_line - 1:end_line] = suggestion_block

        with open(file_path, "w") as f:
            f.writelines(lines)

        print(f"Applied fix to: {file_path} (lines {start_line}-{end_line})")
        return True

    except Exception as e:
        print(f"Error applying fix to {file_path}: {str(e)}")
        return False


import glob


def commit_and_push_changes(branch_name="auto-tf-fix", ignore_paths=None):
    ignore_paths = ignore_paths or []

    print(f"\nPreparing to create/reset branch: `{branch_name}`")

    os.system("git config user.name 'terraform-bot'")
    os.system("git config user.email 'bot@example.com'")
    os.system("git fetch origin")

    branch_exists = os.system(
        f"git ls-remote --exit-code --heads origin {branch_name} > /dev/null"
    ) == 0

    if branch_exists:
        print(f" Remote branch `{branch_name}` exists. Deleting it...")
        os.system(f"git push origin --delete {branch_name}")

    os.system(f"git checkout -B {branch_name}")

    print("Adding all files except ignored patterns...")
    os.system("git add .")

    # Automatically detect correct folder for ignored files
    expanded_ignores = []
    for pattern in ignore_paths:
        # Search recursively inside the entire repo starting from CODE_PATH
        matches = glob.glob(os.path.join(CODE_PATH, "**", pattern), recursive=True)

        if matches:
            for m in matches:
                expanded_ignores.append(m)
                print(f" - Auto-ignoring detected file: {m}")
        else:
            # No match detected, fallback to root-level path
            fallback = os.path.join(CODE_PATH, pattern)
            expanded_ignores.append(fallback)
            print(f" - No matches found. Ignoring fallback: {fallback}")

    # Unstage all matching files before commit
    for path in expanded_ignores:
        os.system(f"git reset HEAD -- '{path}'")

    commit_result = os.system(
        "git commit -m 'Auto-fixed Terraform configuration errors'"
    )

    if commit_result != 0:
        print("No changes to commit. Skipping push.")
        return

    os.system(f"git push -f origin {branch_name}")


def setup_git_remote():
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    if token and repo:
        remote_url = f"https://x-access-token:{token}@github.com/{repo}.git"
        os.system(f"git remote set-url origin {remote_url}")
    else:
        print("GITHUB_TOKEN or GITHUB_REPOSITORY not set")


def main():
    commit_branch = os.getenv("BRANCH_NAME", "auto-tf-fix")
    auto_fix = os.getenv("AUTO_FIX", "true").lower() == "true"

    print("Starting Terraform error analysis and auto-fix...")

    # Read logs
    log_content = read_terraform_logs()
    if "No logs found." in log_content:
        print("No Terraform logs found. Exiting.")
        return

    print("Terraform logs found. Analyzing with AI...")

    # Get AI feedback
    ai_response = get_ai_feedback(log_content)
    if ai_response.startswith("Error calling OpenAI API"):
        print(f"{ai_response}")
        return

    print("AI Analysis Complete:")
    print("=" * 60)
    print(ai_response)
    print("=" * 60)

    # Extract and apply fixes
    fixes = extract_code_fixes(ai_response)
    print(f"\nFound {len(fixes)} fixes to apply")

    successful_fixes = 0
    for i, fix in enumerate(fixes, 1):
        print(f"\nApplying fix {i}/{len(fixes)}: {fix['block_name']} in {fix['file']}")
        if apply_fixes_to_file(fix):
            successful_fixes += 1

    print(f"\nSuccessfully applied {successful_fixes}/{len(fixes)} fixes")
    
    # Set GitHub Action outputs
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"fixes-applied={successful_fixes}\n")
            f.write(f"analysis-summary={ai_response[:500]}...\n")

    # Commit and push if any fixes were applied and auto_fix is enabled
    if successful_fixes > 0 and auto_fix:
        print("\nCommitting and pushing changes...")
        setup_git_remote()
        commit_and_push_changes(commit_branch, ignore_paths=[
            "init_output.txt",
            "plan_*.txt",
            "tfplan.json"
        ])
    elif successful_fixes > 0:
        print(f"\n{successful_fixes} fixes available but auto-fix is disabled")
    else:
        print("\nNo fixes were applied - skipping git operations")

    # Write summary
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        try:
            with open(summary_path, "a") as f:
                f.write("### Terraform AI Analysis Results\n\n")
                f.write(f"**Fixes Found:** {len(fixes)}\n")
                f.write(f"**Fixes Applied:** {successful_fixes}\n\n")
                f.write("#### AI Analysis:\n")
                f.write("```\n")
                f.write(ai_response)
                f.write("\n```\n")
                if successful_fixes > 0 and auto_fix:
                    f.write(f"\n>Auto-fix completed! Pull the '{commit_branch}' branch and review the code locally.\n")
                elif successful_fixes > 0:
                    f.write(f"\n>{successful_fixes} fixes identified but auto-fix is disabled. Enable auto-fix to apply changes automatically.\n")
                else:
                    f.write(f"\n>No fixes could be applied automatically. Manual intervention may be required.\n")
            print("GitHub summary updated")
        except Exception as e:
            print(f"Could not write GitHub summary: {e}")


if __name__ == "__main__":
    main()
