import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = "gpt-4o"
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2" 
OPENAI_EMBED_MODEL = "text-embedding-3-large" 

DATA_DIR = "data/input"
OUTPUT_DIR = "data/output"

