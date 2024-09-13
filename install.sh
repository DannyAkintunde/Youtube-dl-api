#!/bin/bash

# Update package list
apt update

# Install FFmpeg
apt install -y ffmpeg

# Verify installation
ffmpeg -version