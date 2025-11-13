import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

CSV_PATH = "../hospitals.csv"
FAISS_INDEX_PATH = "hospital_faiss.index"
METADATA_PATH = "hospital_metadata.pkl"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K_RESULTS = 3

ASR_PROVIDER = "openai"  # Options: "openai", "gemini", "elevenlabs"
TTS_PROVIDER = "openai"  # Options: "openai", "gemini", "elevenlabs"

AUDIO_SAMPLE_RATE = 16000
AUDIO_FORMAT = "wav"