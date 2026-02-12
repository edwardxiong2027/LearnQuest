#!/bin/bash
# LearnQuest Shutdown Script

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$SCRIPT_DIR/.pids"

echo "============================================"
echo "   Stopping LearnQuest..."
echo "============================================"
echo ""

# Stop Flask
if [ -f "$PID_DIR/flask.pid" ]; then
    FLASK_PID=$(cat "$PID_DIR/flask.pid")
    if kill -0 $FLASK_PID 2>/dev/null; then
        kill $FLASK_PID 2>/dev/null
        echo "  ✓ Flask server stopped."
    else
        echo "  Flask server was not running."
    fi
    rm -f "$PID_DIR/flask.pid"
else
    # Try to find and kill Flask by port
    FLASK_PID=$(lsof -ti:5001 2>/dev/null)
    if [ ! -z "$FLASK_PID" ]; then
        kill $FLASK_PID 2>/dev/null
        echo "  ✓ Flask server stopped."
    else
        echo "  Flask server was not running."
    fi
fi

# Stop Ollama (only if we started it)
if [ -f "$PID_DIR/ollama.pid" ]; then
    OLLAMA_PID=$(cat "$PID_DIR/ollama.pid")
    if kill -0 $OLLAMA_PID 2>/dev/null; then
        kill $OLLAMA_PID 2>/dev/null
        echo "  ✓ Ollama stopped."
    else
        echo "  Ollama was not running."
    fi
    rm -f "$PID_DIR/ollama.pid"
else
    echo "  Ollama was not started by LearnQuest (leaving it running)."
fi

echo ""
echo "============================================"
echo "   LearnQuest stopped."
echo "   Safe to remove USB."
echo "============================================"
