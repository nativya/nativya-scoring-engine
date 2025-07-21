import re
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer, util
from simhash import Simhash
import torch

from .config import settings
from .models import ChatTurn

class ChatScorer:
    """
    Encapsulates all the logic for PII scrubbing and scoring of chat data.
    """
    def __init__(self):
        # Initialize the sentence transformer model
        self.model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
        # Regex for finding emails and phone numbers
        self.email_regex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        self.phone_regex = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?[\d\s-]{7,10}")

    def scrub_pii(self, text: str) -> bool:
        """
        Checks if the text contains any PII (emails or phone numbers).
        Returns True if the text is clean, False otherwise.
        """
        if self.email_regex.search(text) or self.phone_regex.search(text):
            return False
        return True

    def calculate_complexity(self, text: str) -> float:
        """
        Calculates a complexity score based on lexical diversity and average word length.
        """
        tokens = word_tokenize(text.lower())
        if not tokens:
            return 0.0

        # Lexical diversity
        lexical_diversity = len(set(tokens)) / len(tokens) if tokens else 0.0

        # Average word length
        avg_word_length = sum(len(word) for word in tokens) / len(tokens) if tokens else 0.0
        
        # Simple weighted score
        score = (0.6 * lexical_diversity) + (0.4 * (avg_word_length / 10)) # Normalize length score
        return min(score, 1.0)


    def calculate_quality(self, turn: ChatTurn) -> float:
        """
        Calculates a quality score based on the semantic similarity between the
        user's message and the bot's response.
        """
        # Encode sentences to get their embeddings
        embeddings = self.model.encode([turn.user, turn.bot], convert_to_tensor=True)
        # Compute cosine similarity
        cosine_scores = util.cos_sim(embeddings[0], embeddings[1])
        return cosine_scores.item()

    def calculate_uniqueness_hash(self, turn: ChatTurn) -> str:
        """
        Generates a 64-bit SimHash for the entire conversation turn.
        """
        combined_text = f"{turn.user} {turn.bot}"
        return str(Simhash(combined_text).value)

