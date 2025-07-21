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
    It locates the input data, runs the proof, and writes the output.
    """
    logging.info("Starting Vana Satya Proof Task")
    config = load_config()

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Find the data.json file in the input directory
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
            "attributes": {"error": "data.json not found in /input"},
            "metadata": {}
        }
        output_path = os.path.join(OUTPUT_DIR, "results.json")
        with open(output_path, 'w') as f:
            json.dump(error_proof, f, indent=2)
        sys.exit(1)

    # Initialize and run the proof generation
    proof_generator = RegionalLanguageProof(data_file_path=input_file_path, config=config)
    final_proof = proof_generator.generate_proof()

    # Write the final proof to the output directory
    output_path = os.path.join(OUTPUT_DIR, "results.json")
    with open(output_path, 'w') as f:
        # Use .model_dump_json for Pydantic v2+ for clean JSON output
        f.write(final_proof.model_dump_json(indent=2))

    logging.info(f"Proof successfully generated and saved to {output_path}")
    logging.info(final_proof.model_dump_json(indent=2))

if __name__ == "__main__":
    main()