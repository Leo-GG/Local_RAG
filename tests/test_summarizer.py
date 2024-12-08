import pytest
from src.summarizer import TranscriptSummarizer
from src.file_parser import Transcript, Statement

def test_summarize_basic():
    # Create a test transcript
    transcript = Transcript(statements=[
        Statement("TEACHER", "Heute sprechen wir über Photosynthese."),
        Statement("SPEAKER_01", "Was ist der wichtigste Teil dieses Prozesses?"),
        Statement("TEACHER", "Der wichtigste Teil ist die Umwandlung von Sonnenlicht in Energie."),
    ])
    
    summarizer = TranscriptSummarizer()
    summary = summarizer.summarize(transcript)
    
    # Basic validation
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert "Hauptthemen" in summary
    assert "Wichtige Fragen" in summary
    assert "Zentrale Erkenntnisse" in summary
    assert any(["Photosynthese" in line for line in summary.split('\n')])

def test_summarize_empty_transcript():
    transcript = Transcript(statements=[])
    
    summarizer = TranscriptSummarizer()
    with pytest.raises(ValueError, match="Leeres Transkript"):
        summarizer.summarize(transcript) 