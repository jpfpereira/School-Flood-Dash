# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app

# Make port 8050 available to the world outside this container
EXPOSE 8050

# Define environment variable to run in production mode
ENV DASH_ENV=production

# Run app.py when the container launches
CMD ["python", "app.py"]
