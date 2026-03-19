FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for Stockfish (optional but recommended)
RUN apt-get update && apt-get install -y stockfish && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 10000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]

