#!/bin/bash
# run.sh - Setup Python environment and run main application
# 
# This script:
# 1. Creates a Python virtual environment named 'robotics'
# 2. Activates the virtual environment
# 3. Updates pip to the latest version
# 4. Installs required dependencies from requirements.txt
# 5. Runs the main.py application

# Exit on error
set -e

echo "🔧 Setting up Python environment and running application..."

# Check if virtual environment exists
if [ ! -d "robotics" ]; then
    echo "Creating virtual environment 'robotics'..."
    python3 -m venv robotics
else
    echo "Using existing 'robotics' virtual environment..."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source robotics/bin/activate

# Update pip
echo "Updating pip to latest version..."
pip install -U pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Run the application
echo "Running the application..."
python3 main.py