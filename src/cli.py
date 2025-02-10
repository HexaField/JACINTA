#!/usr/bin/env python3
# src/cli.py

import typer
import uuid
from db import SessionLocal, TaskModel

app = typer.Typer()

def get_tasks_by_status(status: str):
    db = SessionLocal()
    try:
        tasks = db.query(TaskModel).filter(TaskModel.status == status).all()
        return tasks
    finally:
        db.close()

@app.command("list")
def list_tasks(status: str):
    """
    List tasks by status (completed, current, or pending).
    
    Example:
      jacinta list completed
    """
    tasks = get_tasks_by_status(status)
    if not tasks:
        typer.echo("No tasks found.")
    else:
        for task in tasks:
            typer.echo(f"{task.id}: {task.title} [{task.status}] - {task.description}")

@app.command("new")
def new_task():
    """
    Create a new task. Prompts for a task title and description.
    
    Example:
      jacinta new
    """
    title = "test"
    description = "write a python script that prints 'hello world'"
    # title = typer.prompt("Enter task title")
    # description = typer.prompt("Enter task description")
    new_id = str(uuid.uuid4())
    db = SessionLocal()
    try:
        task = TaskModel(id=new_id, title=title, description=description, status="pending")
        db.add(task)
        db.commit()
        typer.echo(f"Created task: {task.id} - {task.title}")
    finally:
        db.close()

@app.command("cancel")
def cancel_task(task_id: str):
    """
    Cancel (delete) a task by its ID.
    
    Example:
      jacinta cancel <task_id>
    """
    db = SessionLocal()
    try:
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if task:
            db.delete(task)
            db.commit()
            typer.echo(f"Cancelled task {task_id}")
        else:
            typer.echo("Task not found.")
    finally:
        db.close()

if __name__ == "__main__":
    app()
