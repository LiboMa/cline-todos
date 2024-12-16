#!/bin/bash

# Remove existing virtual environment if it exists
if [ -d "backend/venv" ]; then
    rm -rf backend/venv
fi

# Create new virtual environment
python3 -m venv backend/venv

# Activate virtual environment and install requirements
source backend/venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# Make run.py executable
chmod +x run.py

# Set PYTHONPATH to include the current directory
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the application
./run.py
