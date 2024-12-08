#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.file_parser import TranscriptParser
from src.summarizer import TranscriptSummarizer
from src.query_engine import QueryEngine

def main():
    # Load example transcript
    transcript_path = Path(__file__).parent / "photosynthesis.txt"
    
    # Parse transcript
    parser = TranscriptParser()
    transcript = parser.parse(transcript_path)
    
    # Generate summary
    summarizer = TranscriptSummarizer()
    summary = summarizer.summarize(transcript)
    
    print("Generated Summary:")
    print("=" * 50)
    print(summary)
    print("=" * 50)
    
    # Initialize query engine
    query_engine = QueryEngine(transcript, summary)
    
    # Example questions
    questions = [
        "Was ist Photosynthese?",
        "Welche Materialien brauchen Pflanzen für die Photosynthese?",
        "Wo findet der Prozess statt?",
    ]
    
    print("\nBeispiel-Fragen:")
    print("=" * 50)
    for question in questions:
        print(f"\nFrage: {question}")
        answer = query_engine.query(question)
        print(f"Antwort: {answer}")

if __name__ == "__main__":
    main() 