# src/task_manager.py
import json
import uuid
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from db import SessionLocal, TaskModel
from langchain.chat_models import init_chat_model
from playwright.sync_api import sync_playwright
from typing import List

# Initialize the local model
model = init_chat_model("deepseek-r1:1.5b", model_provider="ollama")

# Pydantic model for jobs
class Job(BaseModel):
    """Sub-task for completing a task."""
    type: str = Field(description="Type of job (e.g., 'research', 'code', 'ask_user')")
    description: str = Field(description="A detailed description of what needs to be done")
    completed: bool = Field(default=False, description="Whether the job is completed")
    result: str = Field(default="", description="Result of the job (if any)")

class JobList(BaseModel):
    """Wrapper for a list of jobs to be returned by the LLM."""
    jobs: List[Job]

def research_web(query: str):
    """Perform a web search and return results."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"https://www.google.com/search?q={query}")
        results = page.locator("h3").all_inner_texts()
        browser.close()
        return results[:3]  # Return top 3 results

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert AI agent that completes tasks by breaking them into actionable steps.",
        ),
        ("human", "Given the task: {task_description}, generate a list of steps to complete it."),
    ]
)

from typing import List  # Import explicitly

def process_pending_tasks():
    """Process pending tasks by breaking them into jobs and executing them."""
    db = SessionLocal()
    try:
        pending_tasks = db.query(TaskModel).filter(TaskModel.status == "pending").all()
        if not pending_tasks:
            print("No pending tasks to process.")
            return

        for task in pending_tasks:
            print(f"Processing task {task.id}: {task.title}")

            # Mark task as "current" so it is not processed again concurrently
            task.status = "current"
            db.commit()

            # Check if the task already has jobs stored
            jobs = task.get_jobs()
            if not jobs:
                print(f"Generating jobs for task {task.id}...")

                # structured_llm = model.with_structured_output(list[Job], method="json_schema")
                
                # response = structured_llm.invoke(f"Break this task into multiple steps: {task.description}")
                
                # jobs = response.model_dump()  # Convert Pydantic object to dict
                # task.set_jobs(jobs)
                # db.commit()

                structured_llm = model.with_structured_output(JobList, method="json_schema")

                response = structured_llm.invoke(f"Break this task into multiple steps: {task.description}")

                jobsResponse = response.jobs  # Use `.jobs` instead of `.model_dump()`
                task.set_jobs([job.dict() for job in jobsResponse])  # Convert to dict before storing
                db.commit()

            jobs = task.get_jobs()

            # Process each job sequentially
            for job in jobs:
                if job["completed"]:
                    continue  # Skip already completed jobs

                print(f"Executing job: {job['description']} ({job['type']})")

                if job["type"] == "research":
                    research_result = research_web(job["description"])
                    job["result"] = research_result

                elif job["type"] == "code":
                    code_result = model.invoke(f"Write a Python script for: {job['description']}")
                    job["result"] = code_result

                elif job["type"] == "ask_user":
                    user_response = input(f"User Input Required: {job['description']}\n> ")
                    job["result"] = user_response

                # Mark job as completed
                job["completed"] = True
                task.set_jobs(jobs)
                db.commit()

            # If all jobs are complete, mark the task as completed
            if all(j["completed"] for j in jobs):
                task.status = "completed"
                db.commit()
                print(f"✅ Task {task.id} completed.")

    finally:
        db.close()
