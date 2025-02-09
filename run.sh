# run.sh
#!/bin/bash

echo "🔧 Activating virtual environment..."
source ai-agent-env/bin/activate

# See if Ollama is running
if lsof -i :11434 &> /dev/null;
then
    echo "🦙 Ollama is already running."
else
    echo "🦙 Starting Ollama..."
    ollama serve &
fi

echo "🤖 Running AI task agent..."
python src/runtime.py
