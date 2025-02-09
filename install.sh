#!/bin/bash

# Exit if any command fails
set -e

echo "📦 Installing system dependencies..."
# Install required packages
sudo apt update && sudo apt install -y python3 python3-venv python3-pip git curl

echo "🐍 Setting up virtual environment..."
# Create a virtual environment
python3 -m venv ai-agent-env
source ai-agent-env/bin/activate

echo "📜 Installing Python dependencies..."
pip install --upgrade pip

# agent dependencies
pip install  -qU "langchain[openai]" ollama gitpython playwright scrapy doit apscheduler openai

# server dependencies
pip install fastapi uvicorn typer[all] requests sqlalchemy

# --- Check if Ollama is already installed ---
if command -v ollama >/dev/null 2>&1; then
    echo "🦙 Ollama is already installed. Skipping installation."
else
    echo "🦙 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

ollama pull deepseek-r1:1.5b

# --- Check if Playwright is already installed ---
if command -v playwright >/dev/null 2>&1; then
    echo "📡 Playwright is already installed. Skipping installation."
else
    echo "📡 Installing Playwright..."
    npm install -g playwright
fi

# --- Check if github is already configured ---
if git config --get user.name >/dev/null 2>&1; then
    echo "🔗 GitHub is already configured. Skipping configuration."
else
    echo "🔗 Configuring GitHub..."
    echo "Enter your GitHub username:"
    read GITHUB_USER
    echo "Enter your GitHub personal access token:"
    read -s GITHUB_TOKEN

    git config --global user.name "$GITHUB_USER"
    git config --global user.email "$GITHUB_USER@users.noreply.github.com"

    echo "💾 Saving GitHub token..."
    export GITHUB_TOKEN
    echo "export GITHUB_TOKEN=$GITHUB_TOKEN" >> ~/.bashrc
fi

echo "⚡ Installing GUI..."
cd gui
npm install
cd ..

echo "✅ Installation complete! Run ./run.sh to start the agent."
