#!/bin/bash

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# List of python versions to check
python_versions=("python3.12" "python3.11" "python3.10" "python3.9" "python3.8" "python3.7")

# Create the virtual environment with the first available python version
for version in "${python_versions[@]}"; do
  if command_exists $version; then
    echo "Found $version"
    $version -m venv venv
    break
  fi
done

# Check if venv directory exists to confirm if virtual environment was created
if [ ! -d "venv" ]; then
  echo "No suitable Python version found."
  exit 1
fi

# Activate the virtual environment
source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt
