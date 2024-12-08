# Transcript Summarizer

Ein Tool zur Zusammenfassung und Analyse von Lehrer-Schüler-Interaktionen.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd transcript-summarizer

# Install dependencies
pip install -e .

# Install Ollama (if not already installed)
# Follow instructions at: https://ollama.ai/download

# Pull required model
ollama pull llama3.2
```

## Verwendung

### Als Kommandozeilen-Tool

```bash
python summarize_interactions.py /pfad/zur/transkript.txt
```

### Als Python-Modul

```python
from src.file_parser import TranscriptParser
from src.summarizer import TranscriptSummarizer
from src.query_engine import QueryEngine

# Transkript einlesen
parser = TranscriptParser()
transcript = parser.parse("transkript.txt")

# Zusammenfassung generieren
summarizer = TranscriptSummarizer()
summary = summarizer.summarize(transcript)

# Fragen stellen
query_engine = QueryEngine(transcript, summary)
answer = query_engine.query("Ihre Frage hier?")
```

## Demo

Ein Beispiel finden Sie unter `examples/demo.py`:

```bash
python examples/demo.py
```

## Tests

```bash
pytest
``` 