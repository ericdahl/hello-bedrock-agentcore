# Use Amazon ECR Public Python image for ARM64 (avoids Docker Hub rate limits)
FROM public.ecr.aws/docker/library/python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for the agent
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the FastAPI server
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
