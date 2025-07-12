# Start from a clean Debian image
FROM debian:bookworm-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies in a single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Python and build tools
    build-essential \
    python3-dev \
    python3 \
    python3-pip \
    # Tesseract and language packs
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-heb \
    # **NEW**: Libraries needed to build Pillow from source
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Specify the command to run on container start
CMD ["python3", "bot.py"]
