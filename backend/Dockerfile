FROM python:3.10-slim

# system deps required for building wheels and psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ libpq-dev libssl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements & install
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Expose (optional, for readability)
EXPOSE 10000

# Use the PORT env var provided by Render; default to 10000 locally.
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-10000} app:app"]
