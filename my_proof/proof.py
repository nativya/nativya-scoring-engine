import logging
import json
from typing import List, Tuple, Dict,Any
import ijson

from .config import settings
from .models_llm import ChatTurn, ValidationResult, FinalProof
from .scorer import ChatScorer
from my_proof.models.proof_response import ProofResponse

class RegionalLanguageProof:
    """
    Orchestrates the entire data validation process for a single JSON file.
    """
    def __init__(self, config:Dict[str,Any] , data_file_path: str):
        self.data_file_path = data_file_path
        self.config=config
        self.proof_response = ProofResponse(dlp_id=config['dlp_id'])
        self.scorer = ChatScorer()


    def generate_proof(self) -> FinalProof:
        """
        Processes the data file and generates the final proof JSON.
        """
        logging.info(f"Starting proof generation.")

        validation_results: List[ValidationResult] = []
        all_fingerprints = set()
        file_internal_duplicates = 0

        try:
            with open(self.data_file_path, "rb") as f:
                # Use ijson to stream the file and handle large datasets
                conversations = ijson.items(f, 'item')
                for i, conv_json in enumerate(conversations):
                    turn = ChatTurn(**conv_json)
                    
                    # 1. PII Scrubbing
                    is_pii_free = self.scorer.scrub_pii(f"{turn.user} {turn.bot}")
                    
                    # 2. Scoring
                    complexity = self.scorer.calculate_complexity(f"{turn.user} {turn.bot}")
                    quality = self.scorer.calculate_quality(turn)
                    
                    # 3. Uniqueness (SimHash)
                    fingerprint = self.scorer.calculate_uniqueness_hash(turn)
                    if fingerprint in all_fingerprints:
                        file_internal_duplicates += 1
                    all_fingerprints.add(fingerprint)

                    # Store result if it passes basic checks
                    if is_pii_free and complexity > settings.MIN_COMPLEXITY_SCORE and quality > settings.MIN_QUALITY_SCORE:
                        validation_results.append(
                            ValidationResult(
                                conversation_index=i,
                                complexity_score=complexity,
                                quality_score=quality,
                                uniqueness_hash=fingerprint,
                                is_pii_free=is_pii_free,
                            )
                        )
        except (ijson.JSONError, json.JSONDecodeError) as e:
            logging.error(f"Invalid JSON format in {self.data_file_path}: {e}")
            return self.create_error_proof("Invalid JSON format.")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return self.create_error_proof(str(e))

        if not validation_results:
            logging.warning("No valid conversations found in the file.")
            return self.create_error_proof("No valid conversations found.")

        # Aggregate scores for the final proof
        final_quality = sum(r.quality_score for r in validation_results) / len(validation_results)
        total_conversations = len(all_fingerprints) + file_internal_duplicates
        final_uniqueness = (total_conversations - file_internal_duplicates) / total_conversations if total_conversations > 0 else 0

        # The overall score can be a blend of quality and uniqueness
        final_score = (0.7 * final_quality) + (0.3 * final_uniqueness)
        is_valid = final_score > 0.5 # Example validity threshold

        logging.info("Proof generation successful.")

        return FinalProof(
            valid=is_valid,
            score=final_score,
            quality=final_quality,
            uniqueness=final_uniqueness,
            attributes={
                "total_conversations_processed": total_conversations,
                "valid_conversations_count": len(validation_results),
                "file_internal_duplicates": file_internal_duplicates,
                "unique_fingerprints_count": len(all_fingerprints),
                "valid_fingerprints": list(sorted([res.uniqueness_hash for res in validation_results])),
                "min_quality_threshold": settings.MIN_QUALITY_SCORE,
                "min_complexity_threshold": settings.MIN_COMPLEXITY_SCORE,
            }
        )
        
    def create_error_proof(self, error_message: str) -> FinalProof:
        """Creates a proof object for a failed validation."""
        return FinalProof(
            valid=False,
            score=0.0,
            quality=0.0,
            uniqueness=0.0,
            attributes={"error": error_message}
        )

