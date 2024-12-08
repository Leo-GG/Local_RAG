import pytest
from src.query_engine import QueryEngine
from src.file_parser import Transcript, Statement

def test_basic_query():
    # Create a test transcript
    transcript = Transcript(statements=[
        Statement("TEACHER", "Heute sprechen wir über Photosynthese."),
        Statement("SPEAKER_01", "Was ist der wichtigste Teil dieses Prozesses?"),
        Statement("TEACHER", "Der wichtigste Teil ist die Umwandlung von Sonnenlicht in Energie."),
        Statement("SPEAKER_02", "Wo findet dieser Prozess statt?"),
        Statement("TEACHER", "Der Prozess findet in den Chloroplasten der Pflanzenzellen statt."),
    ])
    
    # Create a test summary
    summary = """
    Zusammenfassung:
    
    Hauptthemen:
    - Photosynthese
    - Energieumwandlung in Pflanzen
    
    Wichtige Fragen:
    - Was ist der wichtigste Teil der Photosynthese?
    - Wo findet der Prozess statt?
    
    Zentrale Erkenntnisse:
    - Sonnenlicht wird in Energie umgewandelt
    - Der Prozess findet in Chloroplasten statt
    """
    
    # Initialize query engine
    query_engine = QueryEngine(transcript, summary)
    
    # Test basic question
    answer = query_engine.query("Wo findet die Photosynthese statt?")
    answer_lower = answer.lower()
    assert "chloroplasten" in answer_lower
    assert "pflanzenzellen" in answer_lower
    
def test_out_of_context_query():
    # Create a simple transcript
    transcript = Transcript(statements=[
        Statement("TEACHER", "Heute sprechen wir über Photosynthese.")
    ])
    
    query_engine = QueryEngine(transcript, "Zusammenfassung: Photosynthese")
    
    # Test question not covered in transcript
    answer = query_engine.query("Was ist die Hauptstadt von Frankreich?")
    assert "kann ich basierend auf dem gegebenen kontext nicht beantworten" in answer.lower() 