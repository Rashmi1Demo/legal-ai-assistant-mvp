FROM python:3.11-slim

WORKDIR /app

# Install OCR system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Render provides PORT dynamically
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}