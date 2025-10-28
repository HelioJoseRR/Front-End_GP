# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir \
    flask flask-cors requests Flask-SQLAlchemy argon2-cffi pymysql cryptography

# Expose the default Flask port (for gateway)
EXPOSE 5000

# Environment variables (usadas pelo gateway, mas inofensivas para outros serviços)
ENV FLASK_APP=SmartCity/gateway/api_gateway.py
ENV FLASK_ENV=development
ENV PEPPER=wGlg83O8yizv1eQlkSjBqe

# Não define CMD — o docker-compose vai dizer o que rodar
