#!/bin/bash
if [ ! -d ".venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi
python3 main.py 