import string
from pathlib import Path


# Load custom stopwords from stopwords.txt (same directory as this script)

def load_custom_stopwords() -> set:
    stopwords_path = Path(__file__).parent / "stopwords.txt"
    if not stopwords_path.exists():
        raise FileNotFoundError(f"Missing stopwords.txt at: {stopwords_path}")
    with open(stopwords_path, "r", encoding="utf-8") as f:
        return set(
            line.strip() for line in f
            if line.strip() and not line.startswith("#")
        )



# Load once at top level
STOPWORDS = load_custom_stopwords()
punctuations = string.punctuation + "…" + "¨" + "“" + "”" + "’" + "´"
punctuations = punctuations.replace("'", '')
STOPWORDS = STOPWORDS.union(punctuations)