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

echo "🦙 Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

echo "📡 Installing Playwright browsers..."
playwright install

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

echo "⚡ Installing Bun, Vite, and Electron..."
curl -fsSL https://bun.sh/install | bash
export PATH="$HOME/.bun/bin:$PATH"
bun create vite gui --template react-ts
cd gui
bun install
cd ..

echo "✅ Installation complete! Run ./run.sh to start the agent."
