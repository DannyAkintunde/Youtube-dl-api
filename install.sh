#!/bin/bash

echo "Installing Deps"

python -m pip install -r requirements.txt

echo "Update package list"

apt update

echo "Installing FFmpeg"

apt install -y ffmpeg

# Verify installation
ffmpeg -version

echo "\n\nRun python main.py to run the server on your local machine"