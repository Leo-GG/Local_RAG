#!/usr/bin/env python3
"""
Command-line interface for the transcript summarization and interaction system.

This script provides a CLI for:
- Summarizing transcripts of teacher-student interactions
- Interactively querying the content using natural language
- Managing and continuing from saved sessions

The system uses LLM-based analysis to understand and respond to queries about
the transcript content while maintaining context across conversation sessions.
"""

import sys
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from rich import print
from src.file_parser import TranscriptParser
from src.summarizer import TranscriptSummarizer
from src.query_engine import QueryEngine, OllamaConnectionError
from src.config import Config
from src.utils.config_manager import load_or_create_config, create_default_config
from rich.table import Table
import typer
from src.utils.session import SessionManager

app = typer.Typer()

def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load or create configuration settings.
    
    Args:
        config_path (Optional[Path]): Path to existing config file
        
    Returns:
        Config: Loaded or default configuration object
    """
    if config_path and config_path.exists():
        return Config.parse_file(config_path)
    return Config()

@app.command()
def summarize(
    transcript_path: Path = typer.Argument(..., help="Path to the transcript file"),
    config_path: Optional[Path] = typer.Option(None, help="Path to config file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed logs"),
):
    """
    Summarize a transcript file and enable interactive querying.
    """
    # Load and update config
    config = load_config(config_path)
    config.verbose = verbose
    
    # Validate file exists
    if not transcript_path.exists():
        print("[red]Error:[/red] Transcript file not found!")
        raise typer.Exit(1)
    
    try:
        # Parse transcript
        parser = TranscriptParser()
        transcript = parser.parse(transcript_path)
        
        # Generate summary
        summarizer = TranscriptSummarizer()
        summary = summarizer.summarize(transcript)
        
        # Print summary
        print("\n[bold]Summary:[/bold]")
        print(summary)
        
        try:
            # Start interactive query mode
            query_engine = QueryEngine(transcript, summary, config)
            query_engine.start_interactive(transcript_path)
        except OllamaConnectionError as e:
            print(f"[red]Error:[/red] {str(e)}")
            print("\nPlease make sure Ollama is installed and running:")
            print("1. Install Ollama: https://ollama.ai/download")
            print("2. Start the Ollama server: ollama serve")
            print(f"3. Pull the required model: ollama pull {config.model.model_name}")
            raise typer.Exit(1)
        finally:
            if verbose:
                print("\n[bold]Log file:[/bold]", config.output_dir / "transcript_summary.log")
        
    except Exception as e:
        print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command()
def config(
    create: bool = typer.Option(False, "--create", help="Create default config file"),
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    config_path: Optional[Path] = typer.Option(None, help="Path to config file"),
):
    """Manage configuration settings"""
    if create:
        config_path = config_path or Path.home() / ".transcript-summarizer" / "config.json"
        create_default_config(config_path)
        print(f"[green]Created default configuration at:[/green] {config_path}")
        return
    
    if show:
        config = load_or_create_config(config_path)
        
        # Create a pretty table
        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        # Add model settings
        table.add_row("Model Name", config.model.model_name)
        table.add_row("Temperature", str(config.model.temperature))
        table.add_row("Context Window", str(config.model.context_window))
        table.add_row("Language", config.language)
        table.add_row("Output Directory", str(config.output_dir))
        table.add_row("Verbose Logging", str(config.verbose))
        
        print(table)
        return
    
    print("Use --create to create a default config or --show to view current settings")

@app.command()
def sessions(
    list_all: bool = typer.Option(False, "--list", "-l", help="List all saved sessions"),
    show: Optional[Path] = typer.Option(None, "--show", "-s", help="Show details of a specific session"),
    continue_session: Optional[Path] = typer.Option(None, "--continue", "-c", help="Continue a previous session"),
):
    """Manage saved sessions"""
    config = load_or_create_config()
    session_manager = SessionManager(config.output_dir)
    
    if list_all:
        sessions = session_manager.list_sessions()
        if not sessions:
            print("[yellow]No saved sessions found[/yellow]")
            return
        
        table = Table(title="Saved Sessions")
        table.add_column("Date", style="cyan")
        table.add_column("Transcript", style="green")
        table.add_column("Questions", style="blue")
        
        for session_file in sessions:
            session = session_manager.load_session(session_file)
            table.add_row(
                session.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                str(session.transcript_path),
                str(len(session.questions))
            )
        
        print(table)
        return
    
    if show:
        try:
            session = session_manager.load_session(show)
            print(f"\n[bold]Session from[/bold] {session.start_time}")
            print(f"[bold]Transcript:[/bold] {session.transcript_path}")
            print("\n[bold]Summary:[/bold]")
            print(session.summary)
            print("\n[bold]Questions:[/bold]")
            for qa in session.questions:
                print(f"\nQ: {qa['question']}")
                print(f"A: {qa['answer']}")
        except Exception as e:
            print(f"[red]Error loading session:[/red] {str(e)}")
    
    if continue_session:
        try:
            # Load the previous session
            session = session_manager.load_session(continue_session)
            
            # Load and parse the original transcript
            parser = TranscriptParser()
            transcript = parser.parse(session.transcript_path)
            
            # Initialize query engine with previous session data
            query_engine = QueryEngine(transcript, session.summary, config)
            
            # Load previous questions into history
            query_engine.conversation_history = session.questions
            
            # Show session summary
            print(f"\n[bold]Continuing session from[/bold] {session.start_time}")
            print(f"[bold]Transcript:[/bold] {session.transcript_path}")
            print("\n[bold]Previous questions:[/bold]")
            for qa in session.questions:
                print(f"\nQ: {qa['question']}")
                print(f"A: {qa['answer']}")
            
            # Continue interactive mode
            query_engine.start_interactive(session.transcript_path)
            
        except Exception as e:
            print(f"[red]Error loading session:[/red] {str(e)}")
            raise typer.Exit(1)

if __name__ == "__main__":
    app() 