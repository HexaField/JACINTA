# src/runtime.py
import os
import subprocess
import git
import time
import threading
import uuid

from config import get_config

from langchain.chat_models import ChatOpenAI
from apscheduler.schedulers.background import BackgroundScheduler
from playwright.sync_api import sync_playwright

# FastAPI imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# --- Load configuration ---
cfg = get_config()
repo_url = cfg["repo_url"]
local_repo_path = cfg["local_repo_path"]
openai_api_key = cfg["openai_api_key"]

# --- GitHub token check ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("WARNING: GITHUB_TOKEN is not set. GitHub operations may fail if authentication is required.")

# --- Ensure repository is cloned ---
if not os.path.exists(local_repo_path):
    print(f"Local repository path '{local_repo_path}' does not exist.")
    print(f"Cloning repository from {repo_url} into {local_repo_path}...")
    subprocess.run(["git", "clone", repo_url, local_repo_path], check=True)
else:
    print(f"Repository already exists at '{local_repo_path}'.")

# --- Load the repository using GitPython ---
repo = git.Repo(local_repo_path)

# --- Initialize scheduler and LangChain ---
scheduler = BackgroundScheduler()
llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="llama3", temperature=0.7)

# --- FastAPI server for task management ---
app = FastAPI()

class Task(BaseModel):
    id: str = ""
    title: str
    status: str  # "pending", "current", or "completed"

# In-memory store for tasks
tasks = []

@app.get("/tasks")
def list_tasks(status: str = None):
    if status:
        return [t for t in tasks if t["status"] == status]
    return tasks

@app.post("/tasks")
def create_task(task: Task):
    if not task.id:
        task.id = str(uuid.uuid4())
    tasks.append(task.dict())
    return task

@app.delete("/tasks/{task_id}")
def cancel_task(task_id: str):
    global tasks
    for t in tasks:
        if t["id"] == task_id:
            tasks.remove(t)
            return {"message": f"Task {task_id} cancelled"}
    raise HTTPException(status_code=404, detail="Task not found")

def start_api_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

# Start the FastAPI server in a daemon thread
api_thread = threading.Thread(target=start_api_server, daemon=True)
api_thread.start()

# --- Agent functions ---
def generate_code():
    prompt_text = "Write a Python script that prints 'Hello, AI world!'"
    response = llm.predict(prompt_text)
    file_path = os.path.join(local_repo_path, "generated_script.py")
    with open(file_path, "w") as f:
        f.write(response)
    print("✅ Code generated:", file_path)
    commit_and_push(file_path)

def commit_and_push(file_path):
    repo.index.add([file_path])
    repo.index.commit("Auto-generated code update")
    origin = repo.remote(name="origin")
    origin.push()
    print("🚀 Pushed changes to GitHub.")

def research_web():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://news.ycombinator.com/")
        headlines = page.locator("a.storylink").all_inner_texts()
        print("📰 Found headlines:", headlines[:5])
        browser.close()

def schedule_tasks():
    scheduler.add_job(generate_code, "interval", hours=2)
    scheduler.add_job(research_web, "interval", hours=4)
    scheduler.start()
    print("📅 Task scheduler started.")

def main():
    print("🤖 JACINTA AI Task Agent Runtime Starting...")
    schedule_tasks()
    # Keep the main process alive for scheduled jobs and the API server
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
