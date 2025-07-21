# Use a slim Python base image to reduce the attack surface
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy project files
COPY ./requirements.txt /app/requirements.txt
COPY ./my_proof /app/src

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download the NLTK data required for tokenization
RUN python -m nltk.downloader punkt

# Set the entrypoint to run the src package
# This executes the __main__.py file
ENTRYPOINT ["python", "-m", "my_proof"]
