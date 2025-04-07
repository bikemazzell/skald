#!/bin/bash

# Set the SKALD_ROOT environment variable to the current directory
export SKALD_ROOT=$(pwd)

# Create a config.json from the example if it doesn't exist
if [ ! -f "config.json" ]; then
    echo "Creating config.json from example..."
    cp config.json.example config.json
fi

# Run the tests
python -m pytest tests/ -v
