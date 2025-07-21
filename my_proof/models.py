from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class ChatTurn(BaseModel):
    """
    Represents a single turn in a chatbot conversation.
    """
    user: str = Field(..., description="The user's message.")
    bot: str = Field(..., description="The bot's response.")

class ValidationResult(BaseModel):
    """
    Holds the validation scores and details for a single chat conversation.
    """
    conversation_index: int
    complexity_score: float
    quality_score: float
    uniqueness_hash: str = Field(..., description="SimHash fingerprint for the conversation.")
    is_pii_free: bool

class FinalProof(BaseModel):
    """
    The final JSON output object that will be printed to standard output.
    This structure is based on the Vana Satya proof requirements.
    """
    dlp_id: int = 124 # Example DLP ID
    valid: bool
    score: float
    authenticity: float = 1.0  # Assuming data source is trusted for this example
    ownership: float = 1.0      # Assuming ownership is verified externally
    quality: float
    uniqueness: float
    attributes: Dict[str, Any]
    metadata: Dict[str, Any] = {}
