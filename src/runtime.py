# src/runtime.py
import os
import subprocess
import git
import time
import threading
import uuid

from config import get_config

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

# --- Initialize scheduler ---
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()

# --- Initialize the new ChatGPT 4o mini model ---
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = openai_api_key

from langchain.chat_models import init_chat_model
model = init_chat_model("gpt-4o-mini", model_provider="openai")

# --- FastAPI server for task management ---
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Import database initialization (if using persistent tasks)
from db import SessionLocal, TaskModel, init_db
init_db()

app = FastAPI()

# Pydantic model for FastAPI requests/responses
class Task(BaseModel):
    id: str = ""
    title: str
    status: str  # "pending", "current", or "completed"

@app.get("/tasks")
def list_tasks(status: str = None):
    db = SessionLocal()
    try:
        if status:
            tasks = db.query(TaskModel).filter(TaskModel.status == status).all()
        else:
            tasks = db.query(TaskModel).all()
        # Return a simple dict representation for each task
        return [{"id": t.id, "title": t.title, "status": t.status} for t in tasks]
    finally:
        db.close()

@app.post("/tasks")
def create_task(task: Task):
    db = SessionLocal()
    try:
        # If no ID was provided, generate one
        task_id = task.id if task.id else str(uuid.uuid4())
        new_task = TaskModel(id=task_id, title=task.title, status=task.status)
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return {"id": new_task.id, "title": new_task.title, "status": new_task.status}
    finally:
        db.close()

@app.delete("/tasks/{task_id}")
def cancel_task(task_id: str):
    db = SessionLocal()
    try:
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if task:
            db.delete(task)
            db.commit()
            return {"message": f"Task {task_id} cancelled"}
        raise HTTPException(status_code=404, detail="Task not found")
    finally:
        db.close()

def start_api_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

# Start the FastAPI server in a separate daemon thread
api_thread = threading.Thread(target=start_api_server, daemon=True)
api_thread.start()

# --- Agent functions ---
def generate_code():
    """
    Generate Python code using the new model and save it into the repository.
    """
    prompt_text = "Write a Python script that prints 'Hello, AI world!'"
    # Use the new interface to send a message:
    response = model.invoke(prompt_text)
    
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

# --- NEW: Process pending tasks ---
def process_pending_tasks():
    """Process tasks with status 'pending' by sending their description as a prompt to the LLM."""
    db = SessionLocal()
    try:
        pending_tasks = db.query(TaskModel).filter(TaskModel.status == "pending").all()
        for task in pending_tasks:
            print(f"Processing task {task.id}: {task.title}")
            # Mark the task as "current" so it is not processed again concurrently.
            task.status = "current"
            db.commit()  # Commit status update

            # Use the task description as the prompt for the LLM
            try:
                result = model.invoke(task.description)
                print(f"Task {task.id} processed. Result:\n{result}")
            except Exception as e:
                print(f"Error processing task {task.id}: {e}")
                # Optionally, you might want to revert the status or mark it as failed
                task.status = "pending"
                db.commit()
                continue

            # Mark the task as completed
            task.status = "completed"
            db.commit()
    finally:
        db.close()

# --- Update the scheduler function to include our new task processing job ---
def schedule_tasks():
    process_pending_tasks()  # Process any pending tasks immediately on startup
    scheduler.add_job(generate_code, "interval", hours=2)
    scheduler.add_job(research_web, "interval", hours=4)
    scheduler.add_job(process_pending_tasks, "interval", seconds=60)
    scheduler.start()
    print("📅 Task scheduler started.")

# --- Main function remains the same ---
def main():
    print("🤖 JACINTA AI Task Agent Runtime Starting...")
    schedule_tasks()
    # Keep the main process alive
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
