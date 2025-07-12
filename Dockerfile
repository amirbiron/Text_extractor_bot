# Start from a Python 3.11 base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies, including Tesseract for Hebrew and English
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-heb \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Specify the command to run on container start
CMD ["python", "bot.py"]
