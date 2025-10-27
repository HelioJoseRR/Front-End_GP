# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install dependencies
RUN pip install flask flask-cors requests
RUN pip install Flask-SQLAlchemy
RUN pip install argon2-cffi

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=SmartCity/gateway/api_gateway.py
ENV FLASK_ENV=development
ENV PEPPER=wGlg83O8yizv1eQlkSjBqe

# Run app.py when the container launches
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]