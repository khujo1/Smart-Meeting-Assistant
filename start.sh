#!/bin/bash

# Smart Meeting Assistant Startup Script

echo "🎯 Starting Smart Meeting Assistant..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please copy .env.example to .env and configure your API keys."
    echo "cp .env.example .env"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data uploads static/images

# Start the application
echo "🚀 Starting application on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
python3 app.py
