FROM python:3.10-slim

WORKDIR /app

# Install FFmpeg and system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements_render.txt .
RUN pip install --no-cache-dir -r requirements_render.txt

COPY . .

CMD python app.py
