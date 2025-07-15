# Use the official Python image. This is more reliable for building packages.
FROM python:3.11-bullseye

# Set environment variables for non-interactive installation
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory
WORKDIR /app

# Install Tesseract and its language packs
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-heb \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# The command to run when the container starts
CMD ["python3", "bot.py"]
