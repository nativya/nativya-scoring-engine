# ---- Builder Stage ----
# Use a full Python image to build dependencies
FROM python:3.10 as builder

# Set work directory
WORKDIR /app

# Install build dependencies if any
# RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Copy only requirements first for better caching
COPY requirements.txt .

# Install dependencies into a specific folder
RUN pip install --no-cache-dir --prefix="/install" -r requirements.txt

# Download NLTK data
RUN python -m nltk.downloader -d /install/nltk_data punkt


# ---- Final Stage ----
# Use a slim base image for the final product
FROM python:3.10-slim

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set work directory
WORKDIR /app

# Copy installed packages and NLTK data from the builder stage
COPY --chown=appuser:appuser --from=builder /install /usr/local
# Copy application code
COPY --chown=appuser:appuser my_proof /app/my_proof

# Set NLTK_DATA environment variable so NLTK knows where to find the data
ENV NLTK_DATA=/usr/local/nltk_data

# Switch to non-root user
USER appuser

# Set the entrypoint to run the package
ENTRYPOINT ["python", "-m", "my_proof"]