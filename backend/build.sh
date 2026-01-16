#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Retrain model to ensure compatibility with the current environment
echo "Retraining model..."
python model.py
