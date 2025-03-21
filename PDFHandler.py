import PyPDF2
import io
from typing import List, Optional
import streamlit as st
import re
from transformers import GPT2Tokenizer  # If using transformers
from openai import OpenAI  # Import OpenAI SDK for Deepseek

class PDFHandler:
    def __init__(self, model_name="deepseek-reasoner", max_tokens=4096):
        # Initialize Deepseek client
        self.client = OpenAI(
            api_key=st.secrets["DEEPSEEK_API_KEY"],  # Use your Deepseek API key
            base_url="https://api.deepseek.com"  # Deepseek API base URL
        )
        self.system_prompt = st.secrets["SYSTEM_PROMPT"]  # Retrieve prompt from secrets.toml
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")  # If using transformers
        self.max_sequence_length = 1024  # Maximum sequence length for GPT-2 tokenizer

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in the text."""
        return len(self.tokenizer.encode(text))

    def preprocess_text(self, text: str, max_tokens: int = 15000) -> str:
        """Preprocess text to ensure it fits within the token limit."""
        # Remove extra whitespace and newlines
        text = ' '.join(text.split())
        
        # Remove common PDF artifacts
        text = re.sub(r'Page \d+ of \d+', '', text)
        text = re.sub(r'\[+\s*\]+', '', text)
        text = re.sub(r'\(\s*continued\s*\)', '', text)
        
        # Remove multiple spaces and special characters
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,;:\-\'\"(){}[\]]+', ' ', text)
        
        # Truncate to max tokens (ensure it doesn't exceed the model's max sequence length)
        tokens = self.tokenizer.encode(text)
        if len(tokens) > self.max_sequence_length:
            tokens = tokens[:self.max_sequence_length]
            text = self.tokenizer.decode(tokens)
        
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

    def remove_markdown_formatting(self, text: str) -> str:
        """Remove Markdown formatting from the text."""
        # Remove bold formatting (**text**)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        # Remove headers (###, ##, #)
        text = re.sub(r'#+\s*', '', text)
        # Remove dividers (---)
        text = re.sub(r'---', '', text)
        # Remove bullet points and other Markdown symbols
        text = re.sub(r'-\s*', '', text)
        return text.strip()

    def analyze_contract(self, text: str, language: str = "english") -> str:
        """Analyze contract text using Deepseek API."""
        if not text:
            return "No text provided for analysis."

        lang_instruction = "Respond in Spanish." if language.lower() == "spanish" else "Respond in English."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,  # Use "deepseek-reasoner"
                messages=[
                    {"role": "system", "content": f"{self.system_prompt}\n{lang_instruction}"},
                    {"role": "user", "content": self.preprocess_text(text, max_tokens=15000)}
                ],
                max_tokens=self.max_tokens,
                stream=False
            )
            # Remove Markdown formatting from the response
            plain_text_response = self.remove_markdown_formatting(response.choices[0].message.content)
            return plain_text_response
        except Exception as e:
            return f"Error in contract analysis: {str(e)}"