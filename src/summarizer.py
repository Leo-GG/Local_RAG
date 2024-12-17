"""
Module for implementing RAG-based summarization of transcripts.
"""
from typing import List, Dict
from pathlib import Path
import chromadb
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from .file_parser import Statement, TranscriptParser

class TranscriptSummarizer:
    def __init__(self):
        # Initialize with German-specific model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.llm = Ollama(model="llama3.2")  # Can be configured for different models
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def create_vector_store(self, statements: List[Statement]) -> Chroma:
        """Create a vector store from the transcript statements."""
        texts = [f"{s.speaker}: {s.content}" for s in statements]
        docs = self.text_splitter.create_documents(texts)
        
        return Chroma.from_documents(
            documents=docs,
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )

    def summarize(self, statements: List[Statement]) -> Dict[str, str]:
        """Generate a summary of the transcript."""
        vectorstore = self.create_vector_store(statements)
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever()
        )

        # Generate different aspects of the summary
        summary = {
            "key_topics": self._get_key_topics(qa_chain),
            "student_questions": self._summarize_questions(
                [s for s in statements if s.is_question]
            ),
            "main_conclusions": self._get_main_conclusions(qa_chain)
        }

        return summary

    def _get_key_topics(self, qa_chain: RetrievalQA) -> str:
        """Extract key topics from the discussion."""
        query = """
        Was sind die Hauptthemen dieser Diskussion? 
        Bitte liste die wichtigsten Themen auf.
        """
        return qa_chain.run(query)

    def _summarize_questions(self, questions: List[Statement]) -> str:
        """Summarize the main questions asked by students."""
        if not questions:
            return "Keine Fragen wurden gestellt."
        
        question_texts = [q.content for q in questions]
        return "\n".join(f"- {q}" for q in question_texts)

    def _get_main_conclusions(self, qa_chain: RetrievalQA) -> str:
        """Extract main conclusions from the discussion."""
        query = """
        Was sind die wichtigsten Schlussfolgerungen oder Entscheidungen 
        aus dieser Diskussion?
        """
        return qa_chain.run(query)
