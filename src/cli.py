#!/usr/bin/env python3
# src/cli.py
import typer
import requests

app = typer.Typer()

BASE_URL = "http://127.0.0.1:8000"  # FastAPI server URL

@app.command("list")
def list_tasks(status: str):
    """
    List tasks by status (completed, current, or pending).
    
    Example:
      jacinta list completed
    """
    response = requests.get(f"{BASE_URL}/tasks", params={"status": status})
    if response.ok:
        tasks = response.json()
        if not tasks:
            typer.echo("No tasks found.")
        else:
            for t in tasks:
                typer.echo(f"{t['id']}: {t['title']} [{t['status']}]")
    else:
        typer.echo("Error fetching tasks.")

@app.command("new")
def new_task():
    """
    Create a new task. Prompts for a task title.
    
    Example:
      jacinta new
    """
    title = typer.prompt("Enter task title")
    data = {"id": "", "title": title, "status": "pending"}
    response = requests.post(f"{BASE_URL}/tasks", json=data)
    if response.ok:
        task = response.json()
        typer.echo(f"Created task: {task['id']} - {task['title']}")
    else:
        typer.echo("Error creating task.")

@app.command("cancel")
def cancel_task(task_id: str):
    """
    Cancel a task by its ID.
    
    Example:
      jacinta cancel <task_id>
    """
    response = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    if response.ok:
        typer.echo(f"Cancelled task {task_id}")
    else:
        typer.echo("Error cancelling task. Ensure the task ID is correct.")

if __name__ == "__main__":
    app()
