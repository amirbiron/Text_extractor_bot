# Start from a clean Debian image, which gives us more control
FROM debian:bookworm-slim

# Set environment variables to ensure non-interactive installation
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install Python, pip, and then Tesseract and its language packs
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-eng tesseract-ocr-heb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Specify the command to run on container start
CMD ["python3", "bot.py"]
