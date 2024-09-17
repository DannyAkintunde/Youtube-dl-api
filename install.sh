#!/bin/bash

echo "Installing Deps"

python -m pip install -r requirements.txt

echo "Update package list"

apt update

echo "Installing FFmpeg"

apt install -y ffmpeg

# Verify installation
ffmpeg -version