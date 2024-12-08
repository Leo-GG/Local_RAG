"""
Module for generating structured summaries of transcripts using LLM-based analysis.

This module provides functionality to analyze transcripts and generate structured summaries
using LangChain and Ollama. It extracts key topics, important questions, and main conclusions
from the conversation while maintaining factual accuracy through retrieval-augmented generation.
"""

from typing import List, Dict
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain_core.runnables import RunnablePassthrough
from .file_parser import Transcript
from pydantic import BaseModel, Field
from .utils.progress import show_progress

class SummaryOutput(BaseModel):
    """
    Structured output format for transcript summaries.
    
    Attributes:
        summary (str): A concise overview of the entire transcript's content
        topics (List[str]): Main topics discussed in the conversation
        questions (List[str]): Key questions asked by students
        conclusions (List[str]): Important conclusions or decisions reached
    """
    summary: str = Field(description="A brief summary of the entire transcript")
    topics: List[str] = Field(description="Main topics discussed in the transcript")
    questions: List[str] = Field(description="Important questions asked by students")
    conclusions: List[str] = Field(description="Key conclusions or decisions reached")

class TranscriptSummarizer:
    def __init__(self):
        # Initialize Ollama with the German-capable model
        self.llm = OllamaLLM(model="llama3.2")
        
        # Create output parser with fixing capability
        base_parser = PydanticOutputParser(pydantic_object=SummaryOutput)
        self.parser = OutputFixingParser.from_llm(parser=base_parser, llm=self.llm)
        
        # Create summarization prompt template
        self.prompt = PromptTemplate(
            template="""
            Analysiere das folgende Transkript eines Gesprächs zwischen Lehrer und Schülern.
            
            Transkript:
            {transcript}
            
            {format_instructions}
            
            Erstelle eine strukturierte Zusammenfassung mit den folgenden Punkten:
            1. Eine kurze Zusammenfassung des gesamten Gesprächs (2-3 Sätze)
            2. Liste der Hauptthemen der Diskussion
            3. Liste der wichtigen Fragen der Schüler
            4. Liste der zentralen Erkenntnisse oder Entscheidungen
            
            Die Antwort MUSS dem folgenden JSON-Format entsprechen:
            {{
                "summary": "Eine kurze Zusammenfassung des Gesprächs...",
                "topics": ["Thema 1", "Thema 2", ...],
                "questions": ["Frage 1", "Frage 2", ...],
                "conclusions": ["Erkenntnis 1", "Erkenntnis 2", ...]
            }}
            """,
            input_variables=["transcript"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        # Create chain
        self.chain = self.prompt | self.llm | self.parser
    
    def summarize(self, transcript: Transcript) -> str:
        """
        Generate a structured summary of the transcript.
        
        Args:
            transcript (Transcript): The transcript to summarize
            
        Returns:
            SummaryOutput: Structured summary containing key information
            
        Raises:
            ValueError: If the transcript is empty
            RuntimeError: If LLM processing fails
        """
        if not transcript.statements:
            raise ValueError("Leeres Transkript kann nicht zusammengefasst werden.")
            
        try:
            with show_progress("Generiere Zusammenfassung..."):
                # Get full text from transcript
                full_text = transcript.get_full_text()
                
                # Generate structured summary
                result = self.chain.invoke({"transcript": full_text})
            
            # Format the output
            output = "Zusammenfassung:\n"
            output += "=" * 50 + "\n"
            output += result.summary + "\n\n"
            
            output += "Hauptthemen:\n"
            for topic in result.topics:
                output += f"- {topic}\n"
                
            output += "\nWichtige Fragen:\n"
            for question in result.questions:
                output += f"- {question}\n"
                
            output += "\nZentrale Erkenntnisse:\n"
            for conclusion in result.conclusions:
                output += f"- {conclusion}\n"
            
            return output
            
        except Exception as e:
            raise Exception(f"Fehler bei der Zusammenfassung: {str(e)}") 