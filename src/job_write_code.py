# src/job_write_code.py
import os
import git  # GitPython for handling repository commits
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from config import get_config

# Load configuration for repository details
cfg = get_config()
local_repo_path = cfg["local_repo_path"]
repo = git.Repo(local_repo_path)

# Initialize the local model
model = init_chat_model("deepseek-r1:1.5b", model_provider="ollama")

class CodeOutput(BaseModel):
    """Structured output for code generation."""
    filename: str = Field(description="The suggested filename with extension")
    code: str = Field(description="The actual source code")

code_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            ("You are an AI software developer. You generate code files based on a given description.\n"
             "You must output a structured response in JSON format.\n\n"
             "Rules:\n"
             "- Provide a valid filename with an appropriate extension (e.g., `.py`, `.js`, `.cpp`).\n"
             "- Include only the required code, no explanations.\n"
             "- Use best practices for the specified language.\n"
             "- Assume dependencies should be standard unless otherwise specified.\n\n"
             "Input: {description}")
        ),
        ("human", "{description}"),
    ]
)

def commit_and_push(file_path):
    """Commit and push generated code to the GitHub repository."""
    repo.index.add([file_path])
    repo.index.commit(f"Auto-generated file: {file_path}")
    origin = repo.remote(name="origin")
    origin.push()
    print(f"🚀 Pushed changes to GitHub: {file_path}")

def execute_code_job(job):
    """Executes a 'code' job by generating, saving, and committing code to GitHub."""
    structured_code_model = model.with_structured_output(CodeOutput, method="json_schema")

    print(f"💻 Generating code for: {job['description']}")
    response = structured_code_model.invoke(job["description"])

    filename = response.filename
    code = response.code

    # Validate filename
    if not filename or "." not in filename:
        print("⚠️ Invalid filename generated. Defaulting to 'generated_code.py'.")
        filename = "generated_code.py"

    file_path = os.path.join(local_repo_path, filename)

    # Write code to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"✅ Code written to: {file_path}")

    # Commit and push changes
    commit_and_push(file_path)

    return f"Code file '{filename}' has been created and pushed to GitHub."
