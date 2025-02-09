#!/bin/bash

echo "🔧 Activating virtual environment..."
source ai-agent-env/bin/activate

echo "🦙 Starting Ollama..."
ollama serve &

echo "🤖 Running AI task agent..."
python agent.py
