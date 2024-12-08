from typing import List, Dict
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from rich import print
import requests
from .file_parser import Transcript
from .utils.logging import setup_logging
from .utils.storage import ConversationStorage
from .config import Config
from datetime import datetime
from pathlib import Path
from .utils.session import Session, SessionManager

class OllamaConnectionError(Exception):
    """Raised when cannot connect to Ollama server"""
    pass

class QueryEngine:
    def __init__(self, transcript: Transcript, summary: str, config: Config):
        self.transcript = transcript
        self.summary = summary
        self.config = config
        self.logger = setup_logging(config.output_dir, verbose=config.verbose)
        self.storage = ConversationStorage(config.output_dir)
        self.session_manager = SessionManager(config.output_dir)
        self.conversation_history = []
        self.session_start_time = datetime.now()
        
        # Check Ollama connection
        self._check_ollama_connection()
        
        # Initialize Ollama with config
        self.llm = OllamaLLM(
            model=config.model.model_name,
            temperature=config.model.temperature
        )
        self.embeddings = OllamaEmbeddings(
            model=config.model.model_name
        )
        
        # Create vector store from transcript
        self._create_vector_store()
        
        # Setup query prompt
        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            Basierend auf dem folgenden Kontext, beantworte bitte diese Frage.
            Wenn die Antwort nicht im Kontext zu finden ist, antworte mit:
            "Diese Frage kann ich basierend auf dem gegebenen Kontext nicht beantworten."

            Kontext:
            {context}

            Frage: {question}

            Antwort:
            """
        )
        
        # Create chain using LCEL
        self.chain = self.prompt | self.llm
    
    def _check_ollama_connection(self):
        """Check if Ollama server is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code != 200:
                raise OllamaConnectionError("Ollama server returned error status")
        except requests.exceptions.ConnectionError:
            raise OllamaConnectionError(
                "Could not connect to Ollama server. "
                "Please make sure Ollama is running (ollama serve)"
            )
        
        # Check if model is available
        try:
            response = requests.get(f"http://localhost:11434/api/show/{self.config.model.model_name}")
            if response.status_code != 200:
                self.logger.warning(f"Model {self.config.model.model_name} not found, attempting to pull...")
                self._pull_model()
        except requests.exceptions.RequestException as e:
            raise OllamaConnectionError(f"Error checking model availability: {str(e)}")
    
    def _pull_model(self):
        """Pull the required model"""
        try:
            response = requests.post(
                "http://localhost:11434/api/pull",
                json={"name": self.config.model.model_name}
            )
            if response.status_code != 200:
                raise OllamaConnectionError(f"Failed to pull model {self.config.model.model_name}")
            self.logger.info(f"Successfully pulled model {self.config.model.model_name}")
        except requests.exceptions.RequestException as e:
            raise OllamaConnectionError(f"Error pulling model: {str(e)}")
    
    def _create_vector_store(self):
        """Create FAISS vector store from transcript"""
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Combine transcript and summary for better context
        full_text = self.transcript.get_full_text() + "\n\n" + self.summary
        chunks = text_splitter.split_text(full_text)
        
        # Create vector store
        self.vector_store = FAISS.from_texts(
            chunks,
            self.embeddings
        )
    
    def query(self, question: str) -> str:
        """
        Answer a question about the transcript
        
        Args:
            question: Question to answer
            
        Returns:
            str: Generated answer
        """
        try:
            # Get relevant context
            docs = self.vector_store.similarity_search(question, k=3)
            if not docs:
                return "Diese Frage kann ich basierend auf dem gegebenen Kontext nicht beantworten."
                
            context = "\n".join(doc.page_content for doc in docs)
            
            # Check if context is relevant
            if len(context.strip()) < 10:  # Very short or empty context
                return "Diese Frage kann ich basierend auf dem gegebenen Kontext nicht beantworten."
            
            # Generate answer using the chain
            answer = self.chain.invoke({
                "context": context,
                "question": question
            })
            
            # Save to conversation history
            self.conversation_history.append({
                "question": question,
                "answer": answer,
                "timestamp": datetime.now().isoformat()
            })
            
            return answer.strip()
        except Exception as e:
            self.logger.error(f"Error in query: {str(e)}")
            raise
    
    def start_interactive(self, transcript_path: Path):
        """Start interactive query session"""
        print("\n[bold blue]Fragen-Modus gestartet. Drücken Sie Ctrl+C zum Beenden.[/bold blue]")
        print("Stellen Sie Ihre Fragen zum Transkript:\n")
        
        try:
            while True:
                question = input("> ")
                if not question.strip():
                    continue
                    
                answer = self.query(question)
                print(f"\n{answer}\n")
                
        except KeyboardInterrupt:
            print("\n\n[bold blue]Fragen-Modus beendet.[/bold blue]")
            # Save session before exiting
            session = Session(
                transcript_path=transcript_path,
                start_time=self.session_start_time,
                questions=self.conversation_history,
                summary=self.summary
            )
            self.session_manager.save_session(session)
            print(f"\n[green]Session gespeichert in:[/green] {self.config.output_dir}/sessions") 