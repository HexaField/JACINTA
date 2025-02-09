import os
import subprocess
import git
import time
from langchain.chat_models import ChatOpenAI
from apscheduler.schedulers.background import BackgroundScheduler
from scrapy.crawler import CrawlerProcess
from playwright.sync_api import sync_playwright

# GitHub authentication
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_PATH = "./my_ai_project"

# Ensure repository exists
if not os.path.exists(REPO_PATH):
    subprocess.run(["git", "clone", "https://github.com/YOUR_USERNAME/YOUR_REPO.git", REPO_PATH])

repo = git.Repo(REPO_PATH)
scheduler = BackgroundScheduler()
llm = ChatOpenAI(model_name="llama3", temperature=0.7)

def generate_code():
    """Generates Python code using LangChain."""
    prompt = "Write a Python script that prints 'Hello, AI world!'"
    response = llm.predict(prompt)
    
    file_path = os.path.join(REPO_PATH, "generated_script.py")
    with open(file_path, "w") as f:
        f.write(response)
    
    print("✅ Code generated:", file_path)
    commit_and_push(file_path)

def commit_and_push(file_path):
    """Commits and pushes generated code to GitHub."""
    repo.index.add([file_path])
    repo.index.commit("Auto-generated code update")
    origin = repo.remote(name="origin")
    origin.push()
    print("🚀 Pushed changes to GitHub.")

def research_web():
    """Automates web research with Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://news.ycombinator.com/")
        headlines = page.locator("a.storylink").all_inner_texts()
        print("📰 Found headlines:", headlines[:5])
        browser.close()

def schedule_tasks():
    """Schedules recurring tasks."""
    scheduler.add_job(generate_code, "interval", hours=2)
    scheduler.add_job(research_web, "interval", hours=4)
    scheduler.start()
    print("📅 Task scheduler started.")

if __name__ == "__main__":
    print("🤖 AI Task Agent Starting...")
    schedule_tasks()
    while True:
        time.sleep(60)
