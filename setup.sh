#!/bin/bash

# Upgrade pip
pip install --upgrade pip

# Install packages from requirements.txt
pip install -r requirements.txt

# Install alembic
pip install alembic

# Run alembic migrations
alembic upgrade head

# Set up pre-commit hooks
pre-commit install

echo "Setup complete."
