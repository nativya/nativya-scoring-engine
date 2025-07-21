import logging
import sys

# --- Basic Logging Setup ---
# Configure logging to print to standard output.
# In a containerized environment, logs are typically collected from stdout/stderr.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
