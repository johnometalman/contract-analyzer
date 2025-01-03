import streamlit as st
from PDFHandler import extract_text_from_pdf, generate_contract_analysis

# Streamlit app layout
st.title("Contract Chatbot")

st.write("""
    Upload a contract in PDF format and choose a language for the analysis and translation.
    The bot will analyze and provide key insights from the contract in either English or Spanish.
""")

# File upload
pdf_file = st.file_uploader("Upload a Contract (PDF)", type=["pdf"])

if pdf_file is not None:
    # Extract text from the PDF
    contract_text = extract_text_from_pdf(pdf_file)

    # Display extracted text (optional)
    st.subheader("Extracted Contract Text:")
    st.text_area("Contract Text", contract_text, height=200)

    # Language selection
    language = st.selectbox("Select Output Language", ["English", "Spanish"])

    # Analyze the contract
    if st.button("Analyze Contract"):
        # Adjust language for output
        language_code = 'es' if language == 'Spanish' else 'en'

        # Generate analysis
        analysis = generate_contract_analysis(contract_text, language_code)

        # Display contract analysis
        st.subheader(f"Contract Analysis in {language}:")
        st.write(analysis)
