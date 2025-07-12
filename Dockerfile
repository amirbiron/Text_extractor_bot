# Start from a stable Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Update package lists and install dependencies in a single, clean step
# --no-install-recommends reduces image size
# The final command cleans up apt cache to keep the image small
RUN apt-get update && apt-get install -y --no-install-recommends \
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
