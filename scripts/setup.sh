#!/usr/bin/env bash
# setup.sh — One-click setup for the Socratic Tutor project
# Intended for macOS (Apple Silicon / M1). Run from the project root:
#   bash scripts/setup.sh

set -e  # Exit immediately on any error

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

MODEL_NAME="eurecom-ds/phi-3-mini-4k-socratic"
PYTHON_MIN_VERSION="3.9"

echo "=== Socratic Tutor — Project Setup ==="
echo ""

# ── 1. Check Python version ──────────────────────────────────────────────────
echo "[1/6] Checking Python version..."

if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 is not installed. Please install Python 3.9+ first."
    echo "  brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "ERROR: Python >= $PYTHON_MIN_VERSION is required (found $PYTHON_VERSION)."
    exit 1
fi

echo "  Found Python $PYTHON_VERSION — OK"

# ── 2. Create virtual environment ────────────────────────────────────────────
echo "[2/6] Creating virtual environment..."

if [ -d "venv" ]; then
    echo "  Virtual environment already exists — skipping"
else
    python3 -m venv venv
    echo "  Created venv/"
fi

# ── 3. Install Python dependencies ───────────────────────────────────────────
echo "[3/6] Installing Python dependencies..."

source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "  Installed: streamlit, ollama, pandas"

# ── 4. Create required directories ───────────────────────────────────────────
echo "[4/6] Creating project directories..."

mkdir -p logs data
echo "  Created logs/ and data/"

# ── 5. Check Ollama installation ─────────────────────────────────────────────
echo "[5/6] Checking Ollama..."

if ! command -v ollama &> /dev/null; then
    echo ""
    echo "  WARNING: Ollama is not installed."
    echo "  Install it from: https://ollama.com/download"
    echo "  Or run:  brew install ollama"
    echo ""
    echo "  After installing, re-run this script to pull the model."
    exit 1
fi

echo "  Ollama is installed — OK"

# ── 6. Pull the Socratic tutoring model ──────────────────────────────────────
echo "[6/6] Pulling model: $MODEL_NAME ..."
echo "  (This may take a few minutes on the first run)"

ollama pull "$MODEL_NAME"
echo "  Model ready"

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "=== Setup complete ==="
echo ""
echo "To start the application:"
echo "  source venv/bin/activate"
echo "  streamlit run app.py"
echo ""
