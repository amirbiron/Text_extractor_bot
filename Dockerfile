# Start from a specific and stable Python base image
FROM python:3.11-slim-bookworm

# Set environment variables to ensure non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Run update, install tesseract and its language packs, and then clean up
# Using -qq for less verbose output during the build
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-heb \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Specify the command to run on container start
CMD ["python", "bot.py"]
