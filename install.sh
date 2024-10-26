#!/bin/bash

echo "Installing dependencies..."

# Function to install Python
install_python() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Installing Python on Linux..."
        apt update
        apt install -y python3 python3-pip
    elif [[ "$OSTYPE" == "linux-android"* ]]; then
        echo "Installing Python on Termux..."
        apt update
        apt install -y python3 python3-pip
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Installing Python on macOS..."
        brew install python
    elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" ]]; then
        echo "Please install Python manually on Windows."
        exit 1
    else
        echo "Unsupported OS: $OSTYPE"
        exit 1
    fi
}

# Check if Python is installed
if command -v python3 &>/dev/null; then
    echo "Python is already installed."
else
    echo "Python is not installed."
    install_python
fi

if [[ "$OSTYPE" == "linux-android"* ]]; then
    echo "Scraper does not natively support Termux try running it in a virutaul distro"
fi

# Install requirements
python3 -m pip install -r requirements.txt

echo "Downloading scrapers..."

if [ ! -d "scraper" ]; then
    # Clone the repository
    git clone https://github.com/DannyAkintunde/Youtube-dl-scraper scraper
else
    echo "scraper already exists"
    echo "updating scraper..."
    cd scraper
    # pull repo
    git pull
    cd ..
    sleep 1
fi

echo "Installing scraper dependencies..."

# Install dependencies for the scraper
python3 -m pip install -r scraper/requirements.txt

echo "Installing scraper..."

if [ -d "scraper" ] && [ -e "scraper/install.sh" ] && [ -r "scraper/install.sh" ]; then
    chmod +x scraper/install.sh
    ./scraper/install.sh
else
    echo "can't install scraper"
    exit 1
fi

echo "Updating package list..."

# Update package list based on OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    apt update
    echo "Installing FFmpeg..."
    apt install -y ffmpeg
elif [[ "$OSTYPE" == "linux-android"* ]]; then
    apt update
    echo "Installing FFmpeg..."
    apt install -y ffmpeg
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew update
    echo "Installing FFmpeg..."
    brew install ffmpeg
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" ]]; then
    echo "Please install FFmpeg manually on Windows."
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

# Verify installation
ffmpeg -version

sleep 1
echo -e "\n\nRun python3 main.py to run the server on your local machine."