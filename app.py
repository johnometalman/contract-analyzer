import streamlit as st
from PDFHandler import PDFHandler

def main():
    # Initialize PDFHandler
    pdf_handler = PDFHandler()
    
    # Set page configuration
    st.set_page_config(
        page_title="Contract Analysis Chatbot",
        page_icon="📄",
        layout="wide"
    )
    
    # Header
    st.title("Contract Analysis Chatbot")
    st.markdown("Upload a contract (PDF) or paste text for analysis")
    
    # Language selection
    language = st.selectbox(
        "Select response language",
        ["English", "Spanish"],
        index=0
    )
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["Upload PDF", "Paste Text"]
    )
    
    analysis_result = None
    
    if input_method == "Upload PDF":
        uploaded_file = st.file_uploader("Upload your contract (PDF)", type=['pdf'])
        
        if uploaded_file is not None:
            with st.spinner('Extracting text from PDF...'):
                contract_text = pdf_handler.extract_text_from_pdf(uploaded_file)
                st.text_area("Extracted Text", contract_text, height=200)
                
            if st.button("Analyze Contract"):
                with st.spinner('Analyzing contract...'):
                    analysis_result = pdf_handler.analyze_contract(
                        contract_text,
                        language.lower()
                    )
    
    else:  # Paste Text option
        contract_text = st.text_area("Paste your contract text here:", height=300)
        
        if st.button("Analyze Text"):
            with st.spinner('Analyzing text...'):
                analysis_result = pdf_handler.process_text_input(
                    contract_text,
                    language.lower()
                )
    
    # Display results
    if analysis_result:
        st.markdown("### Analysis Results")
        st.markdown(analysis_result)

if __name__ == "__main__":
    main()