import pytest
from pathlib import Path
from src.file_parser import TranscriptParser, Transcript, Statement

def test_parse_valid_transcript(tmp_path):
    # Create a test transcript file
    transcript_content = """
TEACHER:
Hallo zusammen!
SPEAKER_01:
Hallo!
SPEAKER_02:
Wie geht es Ihnen?
TEACHER:
Mir geht es gut, danke.
""".strip()
    
    file_path = tmp_path / "test_transcript.txt"
    file_path.write_text(transcript_content)
    
    # Parse the transcript
    parser = TranscriptParser()
    transcript = parser.parse(file_path)
    
    # Verify the parsing
    assert isinstance(transcript, Transcript)
    assert len(transcript.statements) == 4
    
    # Check first statement
    assert transcript.statements[0] == Statement("TEACHER", "Hallo zusammen!")
    
    # Check student question
    questions = transcript.get_student_questions()
    assert len(questions) == 1
    assert questions[0].text == "Wie geht es Ihnen?"

def test_invalid_format(tmp_path):
    # Create invalid transcript (text before speaker)
    transcript_content = "Invalid line\nTEACHER:\nHallo!"
    
    file_path = tmp_path / "invalid_transcript.txt"
    file_path.write_text(transcript_content)
    
    parser = TranscriptParser()
    with pytest.raises(ValueError, match="Text found before speaker label"):
        parser.parse(file_path)

def test_empty_transcript(tmp_path):
    # Create empty transcript
    file_path = tmp_path / "empty_transcript.txt"
    file_path.write_text("")
    
    parser = TranscriptParser()
    with pytest.raises(ValueError, match="No valid statements found"):
        parser.parse(file_path) 