import re
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer, util
from simhash import Simhash
import torch

from .config import settings
from .models_llm import ChatTurn

class ChatScorer:
    """
    Encapsulates all the logic for PII scrubbing and scoring of chat data.
    """
    def __init__(self):
        self.model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
        self.email_regex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        self.phone_regex = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?[\d\s-]{7,10}")

    # --- ADD THIS FUNCTION ---
    def calculate_word_count_score(self, text: str) -> float:
        """
        Calculates a normalized score based on the word count.
        The score is capped at 1.0.
        """
        word_count = len(word_tokenize(text))
        # Normalize score based on the target, capping at 1.0
        score = min(word_count / settings.TARGET_WORD_COUNT, 1.0)
        return score

    def scrub_pii(self, text: str) -> bool:
        if self.email_regex.search(text) or self.phone_regex.search(text):
            return False
        return True

    def calculate_complexity(self, text: str) -> float:
        tokens = word_tokenize(text.lower())
        if not tokens:
            return 0.0
        lexical_diversity = len(set(tokens)) / len(tokens) if tokens else 0.0
        avg_word_length = sum(len(word) for word in tokens) / len(tokens) if tokens else 0.0
        score = (0.6 * lexical_diversity) + (0.4 * (avg_word_length / 10))
        return min(score, 1.0)

    def calculate_quality(self, turn: ChatTurn) -> float:
        embeddings = self.model.encode([turn.user, turn.bot], convert_to_tensor=True)
        cosine_scores = util.cos_sim(embeddings[0], embeddings[1])
        return cosine_scores.item()

    def calculate_uniqueness_hash(self, turn: ChatTurn) -> str:
        combined_text = f"{turn.user} {turn.bot}"
        return str(Simhash(combined_text).value)