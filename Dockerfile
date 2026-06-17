FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default port (Railway sætter PORT env var)
ENV PORT=5000
EXPOSE $PORT

# Run with gunicorn for production
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 server:app
