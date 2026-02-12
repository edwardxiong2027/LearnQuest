#!/bin/bash
# LearnQuest First-Time Setup Script
# Installs Ollama (if needed), pulls Phi-3, creates Python venv, initializes DB

set -e

# Detect script directory (USB root)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$SCRIPT_DIR/app"
MODELS_DIR="$SCRIPT_DIR/ollama_models"
VENV_DIR="$APP_DIR/venv"
DB_DIR="$APP_DIR/database"
DB_FILE="$DB_DIR/learnquest.db"

echo "============================================"
echo "   LearnQuest Setup"
echo "   USB Path: $SCRIPT_DIR"
echo "============================================"
echo ""

# Step 1: Check/Install Ollama
echo "[1/5] Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "  ✓ Ollama is already installed."
else
    echo "  Ollama not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  Downloading Ollama for macOS..."
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo "  ERROR: Unsupported OS. Please install Ollama manually: https://ollama.com"
        exit 1
    fi
    if command -v ollama &> /dev/null; then
        echo "  ✓ Ollama installed successfully."
    else
        echo "  ERROR: Ollama installation failed. Please install manually."
        exit 1
    fi
fi

# Step 2: Pull Phi-3 model to USB
echo ""
echo "[2/5] Setting up Phi-3 model..."
mkdir -p "$MODELS_DIR"
export OLLAMA_MODELS="$MODELS_DIR"

# Start ollama temporarily if not running
OLLAMA_WAS_RUNNING=false
if pgrep -x "ollama" > /dev/null 2>&1; then
    OLLAMA_WAS_RUNNING=true
    echo "  Ollama is already running."
else
    echo "  Starting Ollama temporarily..."
    ollama serve &> /dev/null &
    OLLAMA_PID=$!
    sleep 3
fi

# Read model from config.json if available
MODEL="phi3"
if [ -f "$SCRIPT_DIR/config.json" ]; then
    CONFIG_MODEL=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/config.json')).get('model','phi3'))" 2>/dev/null)
    if [ ! -z "$CONFIG_MODEL" ]; then
        MODEL="$CONFIG_MODEL"
    fi
fi

echo "  Pulling $MODEL model (this may take a while on first run)..."
ollama pull "$MODEL"
echo "  ✓ $MODEL model ready."

# Stop ollama if we started it
if [ "$OLLAMA_WAS_RUNNING" = false ] && [ ! -z "$OLLAMA_PID" ]; then
    kill $OLLAMA_PID 2>/dev/null || true
fi

# Step 3: Create Python virtual environment
echo ""
echo "[3/5] Setting up Python environment..."
if [ -d "$VENV_DIR" ]; then
    echo "  Virtual environment already exists. Updating..."
else
    echo "  Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
echo "  Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r "$APP_DIR/requirements.txt" -q
echo "  ✓ Python environment ready."
deactivate

# Step 4: Initialize database
echo ""
echo "[4/5] Initializing database..."
mkdir -p "$DB_DIR"
if [ -f "$DB_FILE" ]; then
    echo "  Database already exists. Skipping initialization."
    echo "  (To reset, delete $DB_FILE and run setup again)"
else
    sqlite3 "$DB_FILE" < "$DB_DIR/schema.sql"
    echo "  ✓ Database initialized."
fi

# Step 5: Verify
echo ""
echo "[5/5] Verifying setup..."
ERRORS=0

if ! command -v ollama &> /dev/null; then
    echo "  ✗ Ollama not found"
    ERRORS=$((ERRORS + 1))
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "  ✗ Python venv not found"
    ERRORS=$((ERRORS + 1))
fi

if [ ! -f "$DB_FILE" ]; then
    echo "  ✗ Database not found"
    ERRORS=$((ERRORS + 1))
fi

if [ $ERRORS -eq 0 ]; then
    echo "  ✓ All checks passed!"
    echo ""
    echo "============================================"
    echo "   Setup Complete!"
    echo ""
    echo "   To start LearnQuest:"
    echo "   ./start.sh"
    echo ""
    echo "   Default teacher login:"
    echo "   Name: teacher  PIN: 1234"
    echo "============================================"
else
    echo ""
    echo "  Setup completed with $ERRORS error(s)."
    echo "  Please fix the issues above and run setup again."
    exit 1
fi
