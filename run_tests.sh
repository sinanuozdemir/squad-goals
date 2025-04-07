#!/bin/bash

set -e
set -x

echo "Checking Python version..."
python3 --version || echo "Python3 not found"

echo "Creating virtual environment..."
python3 -m venv test_env || echo "Failed to create venv"

echo "Activating virtual environment..."
source test_env/bin/activate || echo "Failed to activate venv"

echo "Installing dependencies..."
pip install --upgrade pip
pip install -e . || echo "Failed to install squad_goals"

echo "Loading test environment variables..."
if [ -f test.env ]; then
    export $(grep -v '^#' test.env | xargs)
else
    echo "test.env file not found"
fi

echo "Running pytest..."
PYTHONPATH=$(pwd) pytest "$@" || echo "Pytest failed"

echo "Cleaning up..."
deactivate
rm -rf test_env || echo "Failed to remove test_env"

echo "✅ Script completed"
