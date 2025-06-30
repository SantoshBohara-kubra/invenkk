#!/bin/bash

echo "Setting up Mini Amazon Backend..."

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
export DATABASE_URL="sqlite:///mini_amazon.db"
export FLASK_ENV="development"

echo "Backend setup complete!"
echo "To run the backend:"
echo "cd backend && python app.py"
