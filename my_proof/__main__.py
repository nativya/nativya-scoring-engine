import json
import logging
import os
import sys
from typing import Dict, Any

from my_proof.proof import RegionalLanguageProof

INPUT_DIR = "./input"
OUTPUT_DIR = "output"

logging.basicConfig(level=logging.INFO, format='%(message)s')

def load_config() -> Dict[str, Any]:
    """Load proof configuration from environment variables."""
    config = {
        'dlp_id': 145,  # Set your own DLP ID here
        'input_dir': INPUT_DIR,
        'user_email': os.environ.get('USER_EMAIL', None),
    }
    logging.info(f"Using config: {json.dumps(config, indent=2)}")
    return config

def main():
    """
    Main entrypoint for the proof generation process.
    It processes input from TEE request and runs the proof generation.
    """
    logging.info("Starting Vana Satya Proof Task")
    config = load_config()

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Try to read from stdin first (TEE request format)
    input_data = None
    uniqueness_hashes = []
    
    try:
        # Read from stdin for TEE environment
        stdin_input = sys.stdin.read().strip()
        if stdin_input:
            request_data = json.loads(stdin_input)
            logging.info("Processing TEE request format")
            
            # Extract conversation data and uniqueness hashes from request
            conversations = request_data.get("conversations", [])
            uniqueness_hashes = request_data.get("uniqueness_hashes", [])
            
            # Convert prompt/answer format to user/bot format for internal processing
            input_data = []
            for conv in conversations:
                input_data.append({
                    "user": conv.get("prompt", ""),
                    "bot": conv.get("answer", "")
                })
            
            # Update config with request parameters
            if "job_id" in request_data:
                config["job_id"] = request_data["job_id"]
            if "file_id" in request_data:
                config["file_id"] = request_data["file_id"]
            if "nonce" in request_data:
                config["nonce"] = request_data["nonce"]
            
            logging.info(f"Processed {len(input_data)} conversations from TEE request")
            logging.info(f"Received {len(uniqueness_hashes)} uniqueness hashes")
                
    except (json.JSONDecodeError, Exception) as e:
        logging.info(f"No valid stdin input, trying file input: {e}")
    
    # Fallback to file input if stdin didn't work
    if not input_data:
        input_file_path = os.path.join(INPUT_DIR, "data.json")
        
        if not os.path.exists(input_file_path):
            logging.error(f"Input file not found: {input_file_path}")
            # Write an error proof to the output
            error_proof = {
                "dlp_id": config.get("dlp_id", 124),
                "valid": False,
                "score": 0.0,
                "quality": 0.0,
                "uniqueness": 0.0,
                "attributes": {"error": "No input data found - neither stdin nor data.json"},
                "metadata": {}
            }
            output_path = os.path.join(OUTPUT_DIR, "results.json")
            with open(output_path, 'w') as f:
                json.dump(error_proof, f, indent=2)
            sys.exit(1)

        # Initialize and run the proof generation from file
        with open(input_file_path, 'r') as f:
            file_data = json.load(f)
            if isinstance(file_data, list):
                input_data = file_data
            else:
                input_data = file_data.get("conversations", [])
                uniqueness_hashes = file_data.get("uniqueness_hashes", [])
        
        logging.info(f"Loaded {len(input_data)} conversations from file")

    # Create a temporary file for the proof generator if we got data from stdin
    if 'input_file_path' not in locals():
        temp_file_path = os.path.join(INPUT_DIR, "temp_data.json")
        os.makedirs(INPUT_DIR, exist_ok=True)
        with open(temp_file_path, 'w') as f:
            json.dump(input_data, f, indent=2)
        input_file_path = temp_file_path
    
    proof_generator = RegionalLanguageProof(data_file_path=input_file_path, config=config, uniqueness_hashes=uniqueness_hashes)
    final_proof = proof_generator.generate_proof()

    # Write the final proof to the output directory
    output_path = os.path.join(OUTPUT_DIR, "results.json")
    with open(output_path, 'w') as f:
        # Use .model_dump_json for Pydantic v2+ for clean JSON output
        f.write(final_proof.model_dump_json(indent=2))

    logging.info(f"Proof successfully generated and saved to {output_path}")
    logging.info(f"Final proof summary: Valid={final_proof.valid}, Score={final_proof.score:.3f}, Quality={final_proof.quality:.3f}, Uniqueness={final_proof.uniqueness:.3f}")
    
    # Clean up temporary file if created
    if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
        os.remove(temp_file_path)
        logging.info("Cleaned up temporary data file")

if __name__ == "__main__":
    main()

    