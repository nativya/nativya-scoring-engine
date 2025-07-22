# Use a slim Python base image
FROM python:3.10-slim

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set work directory
WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY my_proof /app/my_proof

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Download NLTK data required for tokenization
RUN python -m nltk.downloader punkt

# Set the entrypoint to run the package
ENTRYPOINT ["python", "-m", "my_proof"]