import tomllib
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

with open(ROOT_DIR / "pyproject.toml", "rb") as f:
    config = tomllib.load(f)

COHERE_CONFIG = config["app"]["cohere"]
CHROMA_CONFIG = config["app"]["chromadb"]
GROQ_CONFIG = config["app"]["groq"]
