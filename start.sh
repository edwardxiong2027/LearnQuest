#!/bin/bash
# LearnQuest Launcher
# Starts Ollama + Flask server, opens browser

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$SCRIPT_DIR/app"
MODELS_DIR="$SCRIPT_DIR/ollama_models"
VENV_DIR="$APP_DIR/venv"
PID_DIR="$SCRIPT_DIR/.pids"

mkdir -p "$PID_DIR"

echo "============================================"
echo "   Starting LearnQuest..."
echo "============================================"
echo ""

# Check setup
if [ ! -d "$VENV_DIR" ]; then
    echo "ERROR: Setup not complete. Run ./setup.sh first."
    exit 1
fi

# Set Ollama model path to USB
export OLLAMA_MODELS="$MODELS_DIR"

# Read model from config.json if available
LEARNQUEST_MODEL="phi3"
if [ -f "$SCRIPT_DIR/config.json" ]; then
    CONFIG_MODEL=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/config.json')).get('model','phi3'))" 2>/dev/null)
    if [ ! -z "$CONFIG_MODEL" ]; then
        LEARNQUEST_MODEL="$CONFIG_MODEL"
    fi
fi
export LEARNQUEST_MODEL

# Start Ollama if not running
echo "[1/3] Starting Ollama..."
if pgrep -x "ollama" > /dev/null 2>&1; then
    echo "  Ollama is already running."
else
    ollama serve &> "$SCRIPT_DIR/.ollama.log" &
    echo $! > "$PID_DIR/ollama.pid"
    sleep 2
    echo "  ✓ Ollama started."
fi

# Start Flask
echo "[2/3] Starting LearnQuest server..."
source "$VENV_DIR/bin/activate"
export FLASK_APP="$APP_DIR/server.py"
export LEARNQUEST_DB="$APP_DIR/database/learnquest.db"
export LEARNQUEST_CONTENT="$APP_DIR/content"
export LEARNQUEST_PROMPTS="$APP_DIR/prompts"

cd "$APP_DIR"
python server.py &> "$SCRIPT_DIR/.flask.log" &
FLASK_PID=$!
echo $FLASK_PID > "$PID_DIR/flask.pid"
deactivate
sleep 2

# Check if Flask started successfully
if kill -0 $FLASK_PID 2>/dev/null; then
    echo "  ✓ LearnQuest server started."
else
    echo "  ✗ Server failed to start. Check .flask.log for details."
    exit 1
fi

# Open browser
echo "[3/3] Opening browser..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:5001"
elif command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:5001"
fi

echo ""
echo "============================================"
echo "   LearnQuest is running!"
echo "   Open http://localhost:5001"
echo ""
echo "   To stop: ./stop.sh"
echo "============================================"
