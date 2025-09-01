import os
import re
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VECTOR_DIR = "./rag_db"


# Retrival Function
def build_or_load_vectorstore():
    loader = DirectoryLoader(".", glob="**/*.tf", silent_errors=True)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)

    split_docs = [doc for doc in split_docs if doc.page_content.strip()]

    if not split_docs:
        raise ValueError("No non-empty Terraform content found to embed.")

    embedding = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(split_docs, embedding, persist_directory=VECTOR_DIR)
    return vectordb


def load_existing_vectorstore():
    embedding = OpenAIEmbeddings()
    return Chroma(persist_directory=VECTOR_DIR, embedding_function=embedding)


def retrieve_relevant_context(log_content, top_k=4):
    if not os.path.exists(VECTOR_DIR):
        print("🔄 Building vector store from Terraform code...")
        vectordb = build_or_load_vectorstore()
    else:
        vectordb = load_existing_vectorstore()

    print("🔍 Retrieving relevant context from Terraform files...")
    docs = vectordb.similarity_search(log_content, k=top_k)
    context = "\n\n".join([doc.page_content for doc in docs])
    return context


def read_terraform_logs():
    log_path = "logs/terraform.log"
    if not os.path.exists(log_path):
        return "No logs found."
    with open(log_path, "r") as file:
        return file.read()


# Augumentationa and Generation function
def get_ai_feedback(log_content):
    context = retrieve_relevant_context(log_content)

    prompt = f"""
    You are a Terraform expert and AWS specialist.

    The following is a Terraform failure log. Below that is relevant project context from Terraform configuration files.

    Please:
    - Provide the filename(s) and specific line numbers where the issue occurs.
    - Scan the code first and show if there is error in the code itself. If there is error, provide a complete code block with the fix.
    - No need to show aggregated blocks, just the specific blocks that needs fixing.
    - Read the code base and write a complete code block for every errors that will be fixed.
    - Don't write any variable names, just the code block which has the problem with the fix. Write a complete code block with the fix. I want to see the complete code block with the fix as if I am re-writing all the code.
    - Strictly format your output like this (per issue) without any alterations:

File: path/to/file.tf
Block Name: resource "aws_instance" "example"

[Explanation of the issue]

[Suggested new code block (wrap it in ```hcl```)]


## Terraform Log:
{log_content}

## Project Context:
{context}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "You are a Terraform and AWS expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
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
    suggestion_lines = fix["suggestion"].strip().splitlines()
    suggestion_block = [f"{line}" + "\n" for line in suggestion_lines]

    # lines[fix["start_line"] - 1:fix["end_line"]] = suggestion_block

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
    commit_result = os.system("git commit -m '🤖 Auto-commented problematic Terraform block and suggested fix'")

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