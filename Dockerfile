FROM python:3.12-slim

# Install Git inside the Docker image
RUN apt-get update && apt-get install -y git

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .