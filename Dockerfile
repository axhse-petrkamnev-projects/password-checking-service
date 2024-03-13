# Use an official Python runtime as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script and grant execution permissions
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for storage path
ENV RESOURCE_DIR /data

# Use the entrypoint script to initialize storage and start the Flask app
ENTRYPOINT ["entrypoint.sh"]