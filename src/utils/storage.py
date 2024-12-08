from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List

class ConversationStorage:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def save_summary(self, transcript_path: Path, summary: str):
        """Save generated summary"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.output_dir / f"summary_{timestamp}.txt"
        
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(f"Original transcript: {transcript_path}\n")
            f.write("=" * 50 + "\n")
            f.write(summary)
    
    def save_conversation(self, transcript_path: Path, questions: List[Dict]):
        """Save Q&A history"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        conv_file = self.output_dir / f"conversation_{timestamp}.json"
        
        data = {
            "transcript": str(transcript_path),
            "timestamp": timestamp,
            "questions": questions
        }
        
        with open(conv_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2) 