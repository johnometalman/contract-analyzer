import PyPDF2
import io
from typing import List, Optional
import anthropic
import os
from dotenv import load_dotenv
from pathlib import Path

class PDFHandler:
    def __init__(self):
        # Ensure we're loading from the correct directory
        env_path = Path('.env')
        load_dotenv(dotenv_path=env_path)
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("API key not found. Please ensure your .env file contains ANTHROPIC_API_KEY")
        
        # Initialize the client with the working API key
        self.client = anthropic.Client(api_key=api_key)
        self.system_prompt = os.getenv('SYSTEM_PROMPT', """
            You are a contract analysis expert. Analyze the provided contract and provide the following information:
            1. Contract Type and Purpose
            2. Key Terms and Conditions
            3. Important Dates and Deadlines
            4. Obligations and Responsibilities
            5. Potential Risks or Red Flags
            6. Recommendations
        """)

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from a PDF file."""
        if pdf_file is None:
            return ""
        
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def analyze_contract(self, text: str, language: str = "english") -> str:
        """Analyze contract text using Claude API."""
        if not text:
            return "No text provided for analysis."

        lang_instruction = "Respond in Spanish." if language.lower() == "spanish" else "Respond in English."
        
        try:
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4096,
                messages=[
                    {
                        "role": "system",
                        "content": f"{self.system_prompt}\n{lang_instruction}"
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ]
            )
            
            return message.content[0].text
        except Exception as e:
            return f"Error in contract analysis: {str(e)}"

    def process_text_input(self, text: str, language: str = "english") -> str:
        """Process direct text input."""
        if not text:
            return "No text provided."
        return self.analyze_contract(text, language)