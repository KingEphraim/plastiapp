# Use an official Python runtime as a parent image
FROM python:slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt gunicorn

# Copy the current directory contents into the container at /app
COPY . /app

# Expose port 8080 for Gunicorn to listen on
EXPOSE 8080

# Set the environment variables for Gunicorn and Flask
ENV FLASK_APP=app.py
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:8080 --workers=4 --threads=4 --access-logfile=- --error-logfile=-"

# Run the command to start Gunicorn and the Flask app
CMD ["gunicorn", "app:app"]
