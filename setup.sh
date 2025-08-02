#!/bin/bash

# Setup script for Streamlit Cloud to use Python 3.11
echo "Setting up Python 3.11 environment..."

# Check if Python 3.11 is available
if command -v python3.11 &> /dev/null; then
    echo "Python 3.11 found, creating symlink..."
    ln -sf $(which python3.11) /usr/local/bin/python
    ln -sf $(which python3.11) /usr/local/bin/python3
else
    echo "Python 3.11 not found, using system Python..."
fi

# Verify Python version
python --version
echo "Setup complete!" 