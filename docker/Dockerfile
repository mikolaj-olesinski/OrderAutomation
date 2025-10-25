FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Set working directory to src where app.py is located
WORKDIR /app/src

# Run Flask in development mode with hot reload
CMD ["python", "-u", "app.py"]