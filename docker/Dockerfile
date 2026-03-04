# Use a standard Linux Python image (runs on Windows Home)
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# By default, just keep the container alive or run the script in "test mode"
CMD ["python", "src/main.py"]