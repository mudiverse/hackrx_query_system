import os
import json
import requests
import tempfile
from typing import List, Dict, Any
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document
from app.utils.config import Config
from app.utils.text_utils import clean_text, split_into_clauses, normalize_clause_text

class DocumentIngestionService:
    """Service for ingesting and parsing policy documents."""
    
    def __init__(self):
        self.config = Config()
    
    def download_document(self, url: str) -> str:
        """
        Download document from URL to temporary file.
        
        Args:
            url: URL to the document
            
        Returns:
            Path to temporary file
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=self._get_file_extension(url))
            temp_file.write(response.content)
            temp_file.close()
            
            return temp_file.name
        except Exception as e:
            raise Exception(f"Failed to download document from {url}: {str(e)}")
    
    def _get_file_extension(self, url: str) -> str:
        """Extract file extension from URL."""
        if url.lower().endswith('.pdf'):
            return '.pdf'
        elif url.lower().endswith('.docx'):
            return '.docx'
        elif url.lower().endswith('.doc'):
            return '.doc'
        else:
            # Default to PDF if no extension found
            return '.pdf'
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF using PyMuPDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            doc = fitz.open(file_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            
            doc.close()
            return text
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF {file_path}: {str(e)}")
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """
        Extract text from DOCX using python-docx.
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Extracted text
        """
        try:
            doc = Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text
        except Exception as e:
            raise Exception(f"Failed to extract text from DOCX {file_path}: {str(e)}")
    
    def extract_text_from_document(self, file_path: str) -> str:
        """
        Extract text from document based on file type.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Extracted text
        """
        file_path_lower = file_path.lower()
        
        if file_path_lower.endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        elif file_path_lower.endswith('.docx'):
            return self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
    
    def process_document(self, url: str) -> List[Dict[str, Any]]:
        """
        Process document from URL and extract clauses.
        
        Args:
            url: URL to the policy document
            
        Returns:
            List of clause dictionaries with metadata
        """
        try:
            # Determine if input is a URL or local file path
            is_url = url.lower().startswith("http://") or url.lower().startswith("https://")
            if is_url:
                temp_file_path = self.download_document(url)
                cleanup = True
            else:
                # Assume local file path (absolute or relative)
                temp_file_path = url
                if not os.path.exists(temp_file_path):
                    raise Exception(f"Local file not found: {temp_file_path}")
                cleanup = False
            
            try:
                # Extract text
                raw_text = self.extract_text_from_document(temp_file_path)
                
                # Clean text
                cleaned_text = clean_text(raw_text)
                
                # Split into clauses
                clause_texts = split_into_clauses(cleaned_text)
                
                # Create clause objects
                clauses = []
                for i, clause_text in enumerate(clause_texts):
                    if len(clause_text.strip()) < 50:  # Skip very short clauses
                        continue
                    
                    normalized_text = normalize_clause_text(clause_text)
                    
                    clause_obj = {
                        "clause_id": f"clause_{i+1:04d}",
                        "text": normalized_text,
                        "original_text": clause_text,
                        "length": len(normalized_text),
                        "source_url": url
                    }
                    
                    clauses.append(clause_obj)
                
                # Save clauses to JSON
                self._save_clauses(clauses)
                
                return clauses
                
            finally:
                # Clean up temporary downloaded file only if we created it
                if 'cleanup' in locals() and cleanup and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            raise Exception(f"Failed to process document {url}: {str(e)}")
    
    def _save_clauses(self, clauses: List[Dict[str, Any]]) -> None:
        """
        Save clauses to JSON file.
        
        Args:
            clauses: List of clause dictionaries
        """
        try:
            with open(self.config.CLAUSES_PATH, 'w', encoding='utf-8') as f:
                json.dump(clauses, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"Failed to save clauses: {str(e)}")
    
    def load_clauses(self) -> List[Dict[str, Any]]:
        """
        Load clauses from JSON file.
        
        Returns:
            List of clause dictionaries
        """
        try:
            if not os.path.exists(self.config.CLAUSES_PATH):
                return []
            
            with open(self.config.CLAUSES_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load clauses: {str(e)}")
