from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages all application settings and thresholds using Pydantic.
    Loads settings from a .env file or environment variables.
    """
    # --- Model Configuration ---
    SENTENCE_TRANSFORMER_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"

    # --- Scoring Thresholds ---
    MIN_COMPLEXITY_SCORE: float = 0.2
    MIN_QUALITY_SCORE: float = 0.6
    MIN_LEXICAL_DIVERSITY: float = 0.5
    MIN_WORD_LENGTH: int = 3
    
    # --- ADD THIS LINE ---
    # The word count at which the word count score will be 1.0 (or higher)
    TARGET_WORD_COUNT: int = 100 

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()