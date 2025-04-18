#!/bin/bash
# Exit on error
set -o errexit

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Only after installing dependencies, run database migrations
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"