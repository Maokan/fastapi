# Use Python 3.13 slim image as base
FROM python:3.13

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*
    
# Installing dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    sqlmodel \
    bcrypt \
    jwt \
    asyncio \
    pyjwt \
    python-multipart

# Copy application code
COPY . .

# Create directory for SQLite database
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run the application
CMD [".venv\Scripts\activate","uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
