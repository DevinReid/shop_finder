FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directories for logs
RUN mkdir -p logs

# Default command (will be overridden by Render)
CMD ["python", "email_blaster.py", "send", "5"] 