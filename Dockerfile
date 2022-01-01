# Use the official Python image as the base image
FROM python:3.8.10-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the application code to the container
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install packages from requirements.txt
RUN pip install -r requirements.txt

# Install alembic
RUN pip install alembic


# Expose the port on which FastAPI will run
EXPOSE 8000

# Command to start the FastAPI application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
