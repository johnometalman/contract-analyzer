import openai
import os
from dotenv import load_dotenv
import PyPDF2

# Load environment variables
load_dotenv()

# OpenAI API setup
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load custom prompt from .env file
custom_prompt = os.getenv("CONTRACT_ANALYSIS_PROMPT", "Analyze the following contract text and explain its key points in {language}:\n\n{text}")

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file-like object"""
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

def generate_contract_analysis(text, language='en'):
    """Generate contract analysis using OpenAI API with a custom prompt"""
    prompt = custom_prompt.format(language=language, text=text)

    # Correcting to use openai.ChatCompletion.create (note the capitalization of 'ChatCompletion')
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can use "gpt-4" if available and desired
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500
    )

    return response['choices'][0]['message']['content'].strip()

def translate_text(text, target_language='en'):
    """Translate text to the target language using OpenAI API"""
    prompt = f"Translate the following text to {target_language}:\n\n{text}"

    # Using openai.ChatCompletion.create for translation as well
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can use "gpt-4" if available and desired
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500
    )

    return response['choices'][0]['message']['content'].strip()
