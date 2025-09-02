import os
import re
import hcl2
from openai import OpenAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain.schema import Document

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CODE_PATH = "./"

def retrieve_relevant_context(log_content):
    """
    Extract file references from log and retrieve their content directly from repo
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
- NEVER use "# other configurations..." or "..." or any truncation
- Always provide COMPLETE resource blocks with ALL existing attributes
- Work with ANY AWS resource type (EC2, S3, RDS, Lambda, SQS, etc.)
- Preserve ALL original attributes, nested blocks, and configurations
- Only fix the specific error - keep everything else identical

REQUIRED OUTPUT FORMAT (no deviations):

File: [file_path]
Block Name: [block_type] "[block_name]" 
Issue: [one sentence description]
Solution:
```hcl
[Keep the source code as original as possible to avoid information loss and write complete fixed code block. no lazy writing like other configuration etc.]
```

ANALYSIS RULES:
- Analyze errors in the order they appear in the log
- Include COMPLETE resource blocks in solutions (not partial)
- Only output blocks that contain actual errors
- Use exact file paths from the log
- Maintain ALL original attributes, tags, lifecycle blocks, etc.
- Separate multiple issues with a blank line
- Show the ENTIRE block, not just changed parts

LOG TO ANALYZE:
{log_content}

TERRAFORM FILES:
{context}

Begin systematic analysis with complete resource blocks:"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a Terraform and AWS expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content

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
    file_path = fix["file"]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, "r") as f:
        lines = f.readlines()

    block_type, name1, name2 = parse_block_name(fix['block_name'])
    start_line, end_line = find_block_lines(file_path, block_type, name1, name2)
    
    if start_line is None or end_line is None:
        print(f"Could not find block {fix['block_name']} in {file_path}")
        return
    
    suggestion_lines = fix["suggestion"].strip().splitlines()
    suggestion_block = [f"{line}\n" for line in suggestion_lines]

    lines[start_line - 1:end_line] = suggestion_block

    with open(file_path, "w") as f:
        f.writelines(lines)

    print(f"Applied fix to: {file_path}")

def commit_and_push_changes(branch_name="auto-tf-fix"):
    print(f"\nPreparing to create/reset branch: `{branch_name}`")

    os.system("git config user.name 'terraform-bot'")
    os.system("git config user.email 'bot@example.com'")

    os.system(f"git fetch origin")

    branch_check = os.system(f"git ls-remote --exit-code --heads origin {branch_name} > /dev/null")

    if branch_check == 0:
        print(f" Remote branch `{branch_name}` exists. Deleting it...")
        os.system(f"git push origin --delete {branch_name}")

    os.system(f"git checkout -B {branch_name}")

    os.system("git add .")
    commit_result = os.system("git commit -m '🤖 Auto-fixed Terraform configuration errors'")

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
    commit_branch = "auto-tf-fix"
    log_content = read_terraform_logs()
    if "No logs found." in log_content:
        print("No Terraform logs found. Exiting.")
        return

    ai_response = get_ai_feedback(log_content)
    print("AI Suggestions:\n")
    print(ai_response)

    fixes = extract_code_fixes(ai_response)
    print(f"Found {len(fixes)} fixes to apply")
    
    for fix in fixes:
        apply_fixes_to_file(fix)

    if fixes:
        setup_git_remote()
        commit_and_push_changes(commit_branch)

    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a") as f:
            f.write("### 🔍 AI Suggestions\n\n")
            f.write(ai_response)
            f.write(f"\n\n>Auto-fix applied. Pull the '{commit_branch}' branch and review the code locally.\n")

if __name__ == "__main__":
    main()
