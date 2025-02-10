# src/task_manager.py
import json
import uuid
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from db import SessionLocal, TaskModel
from langchain.chat_models import init_chat_model
from playwright.sync_api import sync_playwright
from typing import List
from enum import Enum
from job_write_code import execute_code_job  # Import the new module

# Initialize the local model
model = init_chat_model("deepseek-r1:1.5b", model_provider="ollama")

class JobType(str, Enum):
    RESEARCH = "research"
    CODE = "code"
    ASK_USER = "ask_user"

# Pydantic model for jobs
class Job(BaseModel):
    """Sub-task for completing a task."""
    type: JobType = Field(description="Type of job. Must be 'research', 'code', or 'ask_user'.")
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
            ("You are an expert AI agent that completes tasks by breaking them into actionable steps.\n"
            "Break this task into multiple steps. Each step must have a valid 'type'.\n\n"
            "Valid types are:\n"
            "- 'research' (for searching the internet for information)\n"
            "- 'code' (for writing or modifying code in any programming language)\n"
            "- 'ask_user' (for requesting input from the user)\n\n"
            "Do NOT use any other types. Each step must be clear and actionable. "
            "Only prompt the user if there is uncertainty about how to complete the task, not for implementation details. "
            "Only research if there is specific information required to complete the task that is not available and that the user does not need to give.\n")
        ),
        ("human", "{task_description}"),
    ]
)

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

                structured_llm = model.with_structured_output(JobList, method="json_schema")

                chain = prompt | structured_llm

                response = chain.invoke(
                    {
                        "task_description": task.description
                    }
                )
                print(f"\nGenerated jobs for task {task.id}: ")
                jobs = response.jobs
                for job in jobs:
                    if job.type not in {"research", "code", "ask_user"}:
                        raise ValueError(f"Unexpected job type: {job.type}")  # Ensure type is valid
                    print(f"- {job.type}: {job.description}")
                task.set_jobs([job.dict() for job in jobs])
                db.commit()
                print("\n")

            jobs = task.get_jobs()

            # Process each job sequentially
            for index, job in enumerate(jobs):  # Use index for direct modification
                if job["completed"]:
                    continue  # Skip already completed jobs

                print(f"Executing job: {job['description']} ({job['type']})")

                if job["type"] == "research":
                    research_result = research_web(job["description"])
                    job["result"] = research_result

                elif job["type"] == "code":
                    job["result"] = execute_code_job(job)  # ✅ Call the function from job_write_code.py

                elif job["type"] == "ask_user":
                    user_response = input(f"User Input Required: {job['description']}\n> ")
                    job["result"] = user_response

                else:
                    print(f"Unknown job type: {job['type']}")

                # ✅ Only mark the specific job as completed
                jobs[index]["completed"] = True  
                task.set_jobs(jobs)
                db.commit()

                # ✅ Save the updated job list back to the database
                task.set_jobs(jobs)
                db.commit()  # Commit after modifying only this job

            # ✅ Now check if all jobs are actually completed before marking the task as completed
            if all(job["completed"] for job in jobs):
                task.status = "completed"
                db.commit()
                print(f"✅ Task {task.id} completed.")

    finally:
        db.close()
