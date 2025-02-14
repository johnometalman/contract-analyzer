import PyPDF2
import io
from typing import List, Optional
import anthropic
import streamlit as st
import re

class PDFHandler:
    def __init__(self, model_name="claude-3-haiku-20240307", max_tokens=20000):
        self.client = anthropic.Client(
            api_key=st.secrets["ANTHROPIC_API_KEY"]
        )
        self.system_prompt = st.secrets.get("SYSTEM_PROMPT", """
            Analyze contracts and provide: 1) Type/Purpose 2) Key Terms 3) Dates 
            4) Obligations 5) Risks 6) Recommendations. Be concise.
        """)
        self.model_name = model_name
        self.max_tokens = max_tokens

    def preprocess_text(self, text: str, max_length: int = 20000) -> str:
        """Preprocess text to reduce token consumption."""
        # Remove extra whitespace and newlines
        text = ' '.join(text.split())
        
        # Remove common PDF artifacts
        text = re.sub(r'Page \d+ of \d+', '', text)
        text = re.sub(r'\[+\s*\]+', '', text)
        text = re.sub(r'\(\s*continued\s*\)', '', text)
        
        # Remove multiple spaces and special characters
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,;:\-\'\"(){}[\]]+', ' ', text)
        
        # Truncate to max length while trying to break at a sentence
        if len(text) > max_length:
            truncated = text[:max_length]
            last_period = truncated.rfind('.')
            if last_period > max_length * 0.8:  # Only use period if it's not too far back
                text = truncated[:last_period + 1]
            else:
                text = truncated
        
        return text.strip()

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract and preprocess text from a PDF file."""
        if pdf_file is None:
            return ""
        
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return self.preprocess_text(text)
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def analyze_contract(self, text: str, language: str = "english") -> str:
        """Analyze contract text using Claude API with optimized token usage."""
        if not text:
            return "No text provided for analysis."

        lang_instruction = "Respond in Spanish." if language.lower() == "spanish" else "Respond in English."
        
        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                system=f"{self.system_prompt}\n{lang_instruction}\nProvide a concise analysis.",
                messages=[
                    {
                        "role": "user",
                        "content": self.preprocess_text(text)
                    }
                ]
            )
            
            return message.content[0].text
        except Exception as e:
            return f"Error in contract analysis: {str(e)}"

    def process_text_input(self, text: str, language: str = "english") -> str:
        """Process direct text input with preprocessing."""
        if not text:
            return "No text provided."
        return self.analyze_contract(text, language)