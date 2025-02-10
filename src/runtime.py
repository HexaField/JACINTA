# src/runtime.py
import os
import subprocess
import git
import time
import threading
import uuid

from config import get_config
from db import SessionLocal, TaskModel, init_db
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler

# --- Load configuration ---
cfg = get_config()
repo_url = cfg["repo_url"]
local_repo_path = cfg["local_repo_path"]

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

# --- Initialize FastAPI ---
init_db()
app = FastAPI()

# Once we have initialized everything, load our task manager
from task_manager import process_pending_tasks

# Pydantic model for API requests/responses
class Task(BaseModel):
    id: str = ""
    title: str
    status: str  # "pending", "current", "completed"

@app.get("/tasks")
def list_tasks(status: str = None):
    """List tasks by status."""
    db = SessionLocal()
    try:
        tasks = db.query(TaskModel).filter(TaskModel.status == status).all() if status else db.query(TaskModel).all()
        return [{"id": t.id, "title": t.title, "status": t.status} for t in tasks]
    finally:
        db.close()

@app.post("/tasks")
def create_task(task: Task):
    """Create a new task."""
    db = SessionLocal()
    try:
        task_id = task.id if task.id else str(uuid.uuid4())
        new_task = TaskModel(id=task_id, title=task.title, status=task.status)
        db.add(new_task)
        db.commit()
        return {"id": new_task.id, "title": new_task.title, "status": new_task.status}
    finally:
        db.close()

@app.delete("/tasks/{task_id}")
def cancel_task(task_id: str):
    """Cancel (delete) a task by ID."""
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

# Start the FastAPI server in a separate daemon thread
def start_api_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

api_thread = threading.Thread(target=start_api_server, daemon=True)
api_thread.start()

# --- Scheduler for processing tasks ---
scheduler = BackgroundScheduler()

def schedule_tasks():
    """Schedule task processing jobs."""
    scheduler.add_job(process_pending_tasks, "interval", seconds=10)
    scheduler.start()
    print("📅 Task scheduler started.")

def main():
    print("🤖 JACINTA AI Task Agent Runtime Starting...")
    schedule_tasks()
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
