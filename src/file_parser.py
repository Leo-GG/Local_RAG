"""
Module for parsing transcript files into structured data.

This module provides classes for parsing and representing transcript files containing
conversations between teachers and students. It handles the extraction of speaker
labels and their corresponding statements while maintaining the chronological order
of the conversation.
"""

from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Statement:
    """
    Represents a single statement in a transcript.
    
    Attributes:
        speaker (str): The identifier of the speaker (e.g., "TEACHER", "SPEAKER_01")
        text (str): The actual content of the statement
    """
    speaker: str
    text: str

@dataclass
class Transcript:
    """
    Represents a complete transcript containing multiple statements.
    
    Attributes:
        statements (List[Statement]): List of all statements in chronological order
    """
    statements: List[Statement]
    
    def get_full_text(self) -> str:
        """
        Returns the complete transcript text with speaker labels.
        
        Returns:
            str: The full transcript text with each statement on a new line
        """
        return "\n".join(f"{s.speaker}: {s.text}" for s in self.statements)
    
    def get_student_questions(self) -> List[Statement]:
        """
        Extracts all questions asked by students in the transcript.
        
        A statement is considered a question if:
        1. The speaker is not "TEACHER"
        2. The text contains a question mark ("?")
        
        Returns:
            List[Statement]: List of all student questions found
        """
        return [
            s for s in self.statements 
            if s.speaker != "TEACHER" and "?" in s.text
        ]

class TranscriptParser:
    """
    Parser for converting transcript files into structured Transcript objects.
    
    The parser expects files to follow a specific format where:
    - Each speaker is identified by a label ending with a colon (e.g., "TEACHER:")
    - The speaker's statement follows on subsequent lines until the next speaker label
    - Empty lines are ignored
    """
    
    def parse(self, file_path: Path) -> Transcript:
        """
        Parse a transcript file into a structured format.
        
        Args:
            file_path (Path): Path to the transcript file
            
        Returns:
            Transcript: A structured representation of the transcript
            
        Raises:
            ValueError: If the file format is invalid or if no valid statements are found
            FileNotFoundError: If the specified file does not exist
            UnicodeDecodeError: If the file encoding is not UTF-8
        """
        statements = []
        current_speaker = None
        current_text = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if line is a speaker label
                if line.endswith(':'):
                    # Save previous statement if exists
                    if current_speaker and current_text:
                        statements.append(Statement(
                            speaker=current_speaker,
                            text=' '.join(current_text)
                        ))
                    # Start new statement
                    current_speaker = line[:-1]  # Remove colon
                    current_text = []
                else:
                    if current_speaker is None:
                        raise ValueError("Invalid format: Text found before speaker label")
                    current_text.append(line)
            
            # Add final statement
            if current_speaker and current_text:
                statements.append(Statement(
                    speaker=current_speaker,
                    text=' '.join(current_text)
                ))
                
        if not statements:
            raise ValueError("No valid statements found in transcript")
            
        return Transcript(statements=statements)