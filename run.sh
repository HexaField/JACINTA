# run.sh
#!/bin/bash

echo "🔧 Activating virtual environment..."
source ai-agent-env/bin/activate

# Force Ollama to stop to avoid port conflicts
sudo systemctl stop ollama

# Start Ollama
echo "🦙 Starting Ollama..."
ollama serve &

echo "🤖 Running AI task agent..."
python src/runtime.py
