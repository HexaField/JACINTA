import os
import subprocess
import git
import time
import sys
import configparser
from langchain.chat_models import ChatOpenAI
from apscheduler.schedulers.background import BackgroundScheduler
from scrapy.crawler import CrawlerProcess
from playwright.sync_api import sync_playwright

def prompt_for_github_repo():
    """
    Prompt the user for a GitHub repository URL.
    The URL must start with 'https://github.com/'.
    """
    repo_url = input(
        "No repository configured. Please enter your GitHub repository URL (e.g., https://github.com/username/repository.git): "
    ).strip()
    if not repo_url.startswith("https://github.com/"):
        print("Invalid repository URL. It should start with 'https://github.com/'. Exiting.")
        sys.exit(1)
    return repo_url

# Set up configuration file (this file should be gitignored)
CONFIG_FILE = "config.ini"
config = configparser.ConfigParser()

# Check if configuration file exists; if not, prompt for repository info and persist it.
if not os.path.exists(CONFIG_FILE):
    repo_url = prompt_for_github_repo()
    # Extract repository name (assumes URL ends with .git)
    repo_name = repo_url.rstrip("/").split("/")[-1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    # Define the local path in the user's Documents folder
    local_repo_path = os.path.join(os.path.expanduser("~"), "Documents", repo_name)
    config["repository"] = {"url": repo_url, "local_path": local_repo_path}
    with open(CONFIG_FILE, "w") as f:
        config.write(f)
    print(f"Configuration saved to {CONFIG_FILE}")
else:
    config.read(CONFIG_FILE)
    if "repository" not in config or "url" not in config["repository"] or "local_path" not in config["repository"]:
        repo_url = prompt_for_github_repo()
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        local_repo_path = os.path.join(os.path.expanduser("~"), "Documents", repo_name)
        config["repository"] = {"url": repo_url, "local_path": local_repo_path}
        with open(CONFIG_FILE, "w") as f:
            config.write(f)
        print(f"Configuration saved to {CONFIG_FILE}")
    else:
        repo_url = config["repository"]["url"]
        local_repo_path = config["repository"]["local_path"]

# GitHub authentication from the environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("WARNING: GITHUB_TOKEN is not set. GitHub operations may fail if authentication is required.")

# Check if the repository exists locally; if not, clone it to the Documents folder.
if not os.path.exists(local_repo_path):
    print(f"Local repository path '{local_repo_path}' does not exist.")
    print(f"Cloning repository from {repo_url} into {local_repo_path}...")
    subprocess.run(["git", "clone", repo_url, local_repo_path], check=True)
else:
    print(f"Repository already exists at '{local_repo_path}'.")

# Load the repository using GitPython
repo = git.Repo(local_repo_path)
scheduler = BackgroundScheduler()
llm = ChatOpenAI(model_name="llama3", temperature=0.7)

def generate_code():
    """
    Generate Python code using LangChain and save it into the repository.
    """
    prompt_text = "Write a Python script that prints 'Hello, AI world!'"
    response = llm.predict(prompt_text)
    
    file_path = os.path.join(local_repo_path, "generated_script.py")
    with open(file_path, "w") as f:
        f.write(response)
    
    print("✅ Code generated:", file_path)
    commit_and_push(file_path)

def commit_and_push(file_path):
    """
    Commit the newly generated code and push it to the GitHub repository.
    """
    repo.index.add([file_path])
    repo.index.commit("Auto-generated code update")
    origin = repo.remote(name="origin")
    origin.push()
    print("🚀 Pushed changes to GitHub.")

def research_web():
    """
    Perform simple web research using Playwright.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://news.ycombinator.com/")
        headlines = page.locator("a.storylink").all_inner_texts()
        print("📰 Found headlines:", headlines[:5])
        browser.close()

def schedule_tasks():
    """
    Schedule tasks for code generation and web research.
    """
    scheduler.add_job(generate_code, "interval", hours=2)
    scheduler.add_job(research_web, "interval", hours=4)
    scheduler.start()
    print("📅 Task scheduler started.")

if __name__ == "__main__":
    print("🤖 AI Task Agent Starting...")
    schedule_tasks()
    # Keep the script running so scheduled jobs can run periodically.
    while True:
        time.sleep(60)
