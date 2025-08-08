import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the application."""

    # Gemini Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_EMBED_MODEL = "models/text-embedding-004"
    GEMINI_GEN_MODEL = "gemini-1.5-flash"

    # FAISS Configuration
    FAISS_INDEX_PATH = "data/faiss_index.bin"
    METADATA_PATH = "data/metadata.pkl"
    CLAUSES_PATH = "data/clauses.json"

    # Data directory
    DATA_DIR = "data"

    @classmethod
    def validate(cls):
        """Validate that required environment variables are set."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        # Create data directory if it doesn't exist
        os.makedirs(cls.DATA_DIR, exist_ok=True)
