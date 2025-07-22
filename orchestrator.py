import os
import sys
import json
import subprocess
import requests
from typing import Dict, Any

# --- Configuration ---
# This should be the name of your Tier 1 Docker image
TIER_1_DOCKER_IMAGE = "vana-satya-proof:latest"

# This is the public URL of your deployed Tier 2 service
TIER_2_API_URL = "https://global-integrity-service.onrender.com"

# The secret API key for your Tier 2 service
TIER_2_API_KEY = os.environ.get("TIER_2_API_KEY", "your-secret-api-key-goes-here")

# --- Score Weighting ---
# How much each score contributes to the final result
QUALITY_WEIGHT = 0.6
GLOBAL_UNIQUENESS_WEIGHT = 0.4


def run_tier_1_proof(input_data_path: str) -> Dict[str, Any]:
    """
    Runs the Tier 1 proof in a Docker container.

    Args:
        input_data_path: The path to the data.json file.

    Returns:
        The parsed JSON output from the Tier 1 proof.
    """
    print("--- Running Tier 1: Local Data Proof ---")
    
    input_dir = os.path.dirname(input_data_path)
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)

    # Docker command to run the proof
    command = [
        "docker", "run", "--rm",
        "-v", f"{os.path.abspath(input_dir)}:/input",
        "-v", f"{os.path.abspath(output_dir)}:/output",
        TIER_1_DOCKER_IMAGE
    ]

    try:
        print(f"Executing Docker command: {' '.join(command)}")
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Tier 1 Docker container.")
        print(f"Stderr: {e.stderr}")
        raise

    # Read the results from the output file
    results_path = os.path.join(output_dir, "results.json")
    if not os.path.exists(results_path):
        print("Error: Tier 1 did not produce a results.json file.")
        raise FileNotFoundError("results.json not found")
        
    with open(results_path) as f:
        tier_1_results = json.load(f)
        
    print("Tier 1 Proof Successful.")
    return tier_1_results


def call_tier_2_service(fingerprints: list[str]) -> Dict[str, Any]:
    """
    Calls the deployed Tier 2 service to get the global uniqueness score.

    Args:
        fingerprints: A list of SimHash fingerprints from Tier 1.

    Returns:
        The parsed JSON response from the Tier 2 API.
    """
    print("\n--- Calling Tier 2: Global Integrity Service ---")
    if not fingerprints:
        print("No valid fingerprints to send. Skipping.")
        return {"global_uniqueness_score": 1.0} # No data is perfectly unique

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": TIER_2_API_KEY
    }
    payload = {"fingerprints": fingerprints}

    try:
        response = requests.post(TIER_2_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status() # Raises an exception for 4xx or 5xx status codes
    except requests.exceptions.RequestException as e:
        print(f"Error calling Tier 2 API: {e}")
        raise

    print("Tier 2 Call Successful.")
    return response.json()


def main(data_file_path: str):
    """
    The main orchestration function.
    """
    # Step 1: Run Tier 1 Proof
    tier_1_results = run_tier_1_proof(data_file_path)
    
    if not tier_1_results.get("valid"):
        print("\nTier 1 proof marked the data as invalid. Halting process.")
        print(f"Reason: {tier_1_results.get('attributes', {}).get('error', 'Unknown')}")
        return

    # Extract necessary info from Tier 1 results
    tier_1_quality = tier_1_results.get("quality", 0.0)
    valid_fingerprints = tier_1_results.get("attributes", {}).get("valid_fingerprints", [])

    # Step 2: Call Tier 2 Service
    tier_2_results = call_tier_2_service(valid_fingerprints)
    global_uniqueness = tier_2_results.get("global_uniqueness_score", 0.0)

    # Step 3: Calculate the Final Overall Score
    print("\n--- Calculating Final Overall Score ---")
    final_score = (tier_1_quality * QUALITY_WEIGHT) + (global_uniqueness * GLOBAL_UNIQUENESS_WEIGHT)

    print("\n--- VALIDATION COMPLETE ---")
    print(f"Tier 1 Quality Score: {tier_1_quality:.3f}")
    print(f"Global Uniqueness Score: {global_uniqueness:.3f}")
    print("---------------------------------")
    print(f"Final Weighted Score: {final_score:.3f}")
    print("---------------------------------")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} /path/to/data.json")
        sys.exit(1)
        
    data_file = sys.argv[1]
    if not os.path.exists(data_file):
        print(f"Error: File not found at {data_file}")
        sys.exit(1)
        
    main(data_file)
