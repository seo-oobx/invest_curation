FROM python:3.11-slim

WORKDIR /app

# Copy the api directory into the container
COPY api/ ./api/

# Install dependencies
WORKDIR /app/api
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (Railway injects PORT env var)
ENV PORT=8000
EXPOSE $PORT

# Command to run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
