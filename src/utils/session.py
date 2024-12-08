"""
Module for managing conversation sessions and their persistence.

This module provides functionality to save, load, and manage conversation sessions,
including their transcripts, questions, answers, and summaries. It handles session
serialization and persistence to enable conversation continuity across runs.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import json

@dataclass
class Session:
    """
    Represents a single conversation session.
    
    Attributes:
        transcript_path (Path): Path to the transcript file used in this session
        start_time (datetime): When the session was started
        questions (List[Dict]): List of question-answer pairs from the session
        summary (str): Generated summary of the transcript
    """
    transcript_path: Path
    start_time: datetime
    questions: List[Dict]
    summary: str

class SessionManager:
    """
    Manages the saving, loading, and listing of conversation sessions.
    
    This class handles the persistence of session data, allowing users to:
    - Save their current session state
    - List all previously saved sessions
    - Load and continue from a previous session
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialize the session manager.
        
        Args:
            output_dir (Path): Base directory for storing session data
        """
        self.sessions_dir = output_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def save_session(self, session: Session):
        """
        Save a session to a JSON file.
        
        The session is saved with a timestamp-based filename to ensure uniqueness.
        
        Args:
            session (Session): The session to save
            
        Raises:
            IOError: If there are issues writing to the file
            TypeError: If session data cannot be serialized to JSON
        """
        timestamp = session.start_time.strftime("%Y%m%d_%H%M%S")
        session_file = self.sessions_dir / f"session_{timestamp}.json"
        
        data = {
            "transcript": str(session.transcript_path),
            "start_time": session.start_time.isoformat(),
            "questions": session.questions,
            "summary": session.summary
        }
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def list_sessions(self) -> List[Path]:
        """
        List all saved session files.
        
        Returns:
            List[Path]: List of paths to saved session files
        """
        return list(self.sessions_dir.glob("session_*.json"))
    
    def load_session(self, session_file: Path) -> Session:
        """
        Load a previously saved session.
        
        Args:
            session_file (Path): Path to the session file to load
            
        Returns:
            Session: The loaded session object
            
        Raises:
            FileNotFoundError: If the session file doesn't exist
            json.JSONDecodeError: If the session file is invalid JSON
            ValueError: If the session data is malformed
        """
        with open(session_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return Session(
            transcript_path=Path(data["transcript"]),
            start_time=datetime.fromisoformat(data["start_time"]),
            questions=data["questions"],
            summary=data["summary"]
        ) 