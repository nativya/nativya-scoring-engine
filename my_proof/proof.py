import logging
import json
from typing import List, Any, Dict
import ijson

from .config import settings
from .models_llm import ChatTurn, ValidationResult, FinalProof
from .scorer import ChatScorer

class RegionalLanguageProof:
    """
    Orchestrates the entire data validation process for a single JSON file.
    """
    def __init__(self, config: Dict[str, Any], data_file_path: str, uniqueness_hashes: List[str] = None):
        self.data_file_path = data_file_path
        self.config = config
        self.scorer = ChatScorer()
        # Note: External uniqueness hashes are handled by frontend, not used for scoring
        self.external_uniqueness_hashes = set(uniqueness_hashes) if uniqueness_hashes else set()

    def generate_proof(self) -> FinalProof:
        """
        Processes the data file and generates the final proof JSON.
        """
        logging.info("Starting proof generation.")

        validation_results: List[ValidationResult] = []
        # --- RE-INTRODUCED UNIQUENESS TRACKING ---
        all_fingerprints = set()
        file_internal_duplicates = 0
        all_word_count_scores = [] 

        try:
            with open(self.data_file_path, "rb") as f:
                conversations = ijson.items(f, 'item')
                for i, conv_json in enumerate(conversations):
                    turn = ChatTurn(**conv_json)
                    combined_text = f"{turn.user} {turn.bot}"
                    
                    is_pii_free = self.scorer.scrub_pii(combined_text)
                    complexity = self.scorer.calculate_complexity(combined_text)
                    quality = self.scorer.calculate_quality(turn)
                    word_count_score = self.scorer.calculate_word_count_score(combined_text)
                    
                    all_word_count_scores.append(word_count_score)

                    # --- CALCULATE AND CHECK UNIQUENESS HASH ---
                    fingerprint = self.scorer.calculate_uniqueness_hash(turn)
                    if fingerprint in all_fingerprints:
                        file_internal_duplicates += 1
                    all_fingerprints.add(fingerprint)

                    # Add conversation to the valid list if it passes basic checks
                    if (is_pii_free and 
                        complexity > settings.MIN_COMPLEXITY_SCORE and 
                        quality > settings.MIN_QUALITY_SCORE):
                        
                        validation_results.append(
                            ValidationResult(
                                conversation_index=i,
                                complexity_score=complexity,
                                quality_score=quality,
                                uniqueness_hash=fingerprint, # Store the hash per result
                                is_pii_free=is_pii_free,
                            )
                        )
        except (ijson.JSONError, json.JSONDecodeError) as e:
            return self.create_error_proof(f"Invalid JSON format: {e}")
        except Exception as e:
            return self.create_error_proof(f"An unexpected error occurred: {e}")

        if not validation_results:
            return self.create_error_proof("No valid conversations found.")

        # --- UPDATED FINAL SCORE CALCULATION WITH UNIQUENESS ---
        final_quality = sum(r.quality_score for r in validation_results) / len(validation_results)
        
        total_conversations = len(all_fingerprints)
        # Calculate intra-file uniqueness score
        # --- INTRA-FILE UNIQUENESS CALCULATION ONLY ---
        # Only check for duplicates within the current file/request
        if total_conversations == 0:
            final_uniqueness = 0.0
        else:
            # Uniqueness is the ratio of unique conversations to total conversations
            # Only penalize internal duplicates within this request
            unique_conversations = total_conversations - file_internal_duplicates
            final_uniqueness = max(0.0, unique_conversations / total_conversations)

        
        final_word_count_score = sum(all_word_count_scores) / len(all_word_count_scores) if all_word_count_scores else 0

        # The final score is now a blend of quality, uniqueness, and word count
        # Improved weights: 40% quality, 40% uniqueness, 20% word count
        final_score = (0.4 * final_quality) + (0.4 * final_uniqueness) + (0.2 * final_word_count_score)
        is_valid = final_score > 0.5 and len(validation_results) > 0

        logging.info("Proof generation successful.")

        return FinalProof(
            valid=is_valid,
            score=final_score,
            quality=final_quality,
            uniqueness=final_uniqueness, # Report the calculated uniqueness
            attributes={
                "total_conversations_processed": total_conversations,
                "valid_conversations_count": len(validation_results),
                "file_internal_duplicates": file_internal_duplicates,
                "unique_fingerprints_count": len(all_fingerprints),
                "average_word_count_score": final_word_count_score,
                "final_quality_score": final_quality,
                "final_uniqueness_score": final_uniqueness,
                "min_quality_threshold": settings.MIN_QUALITY_SCORE,
                "min_complexity_threshold": settings.MIN_COMPLEXITY_SCORE,
                "target_word_count": settings.TARGET_WORD_COUNT,
            },
            # Provide all fingerprints for the higher-level Inter-File check
            metadata={
                "all_uniqueness_hashes": list(sorted(all_fingerprints))
            }
        )
        
    def create_error_proof(self, error_message: str) -> FinalProof:
        """Creates a proof object for a failed validation."""
        return FinalProof(
            valid=False, score=0.0, quality=0.0, uniqueness=0.0,
            attributes={"error": error_message},
            metadata={}
        )