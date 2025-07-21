from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages all application settings and thresholds using Pydantic.
    Loads settings from a .env file or environment variables.
    """
    # --- Model Configuration ---
    # The name of the sentence-transformer model to use for quality scoring.
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"

    # --- Scoring Thresholds ---
    # These values determine the minimum acceptable scores for data validation.
    MIN_COMPLEXITY_SCORE: float = 0.2
    MIN_QUALITY_SCORE: float = 0.6
    MIN_LEXICAL_DIVERSITY: float = 0.5
    MIN_WORD_LENGTH: int = 3

    # Pydantic settings configuration
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Create a single settings instance to be used throughout the application
settings = Settings()
