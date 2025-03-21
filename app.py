import streamlit as st
import os
import time  # Import time for the spinner timer
from PDFHandler import PDFHandler

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Contract Analyzer App",
        page_icon="📄",
        layout="wide"
    )
    
    # Header
    st.title("Contract Analyzer App")
    st.write('###### ❤️ Made with love by [Johnometalman](https://www.johnometalman.me/)')
    st.divider()

    st.markdown(
    """
    ##### Instructions of Use
    1. Upload the contract in PDF or Text
    2. Choose the number of tokens you want on the left pannel
    3. Select Analyze Contract

    This application is completely free to use, so you don't need to worry about tokens.<br>
    The cache is cleared once you stop using the app or clicking the button **Clear Contract**
    
    This is the **2nd version** of this app.
    """, unsafe_allow_html=True
    )

    st.divider()
    
    # Sidebar for configurations
    st.sidebar.header("Configuration.. if you want")
    
    # Token limit selection
    max_tokens = st.sidebar.slider(
        "Max Response Tokens (Higher = More Detailed, More Cost)",
        min_value=250,
        max_value=4096,
        value=1000,
        step=250
    )
    
    # Initialize PDFHandler with selected configuration
    pdf_handler = PDFHandler(max_tokens=max_tokens)
    
    # Main content
    st.markdown("**Upload a contract (PDF) or paste text for analysis**")
    
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
    
    st.sidebar.markdown("""
    #### Disclaimer
    - This app is trained with general information about contracts.
                        
    - The AI Model used is Deepseek Reasoning 
                        
    - Use this tool as a recommendation and **not as a legal advisor**.
    """)
    
    # Initialize session state variables
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    if "contract_text" not in st.session_state:
        st.session_state.contract_text = ""
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    
    if input_method == "Upload PDF":
        uploaded_file = st.file_uploader("Upload your contract (PDF)", type=['pdf'])
        
        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file  # Save uploaded file to session state
            with st.spinner('Extracting and preprocessing text...', show_time=True):
                contract_text = pdf_handler.extract_text_from_pdf(uploaded_file)
                st.session_state.contract_text = contract_text  # Save extracted text to session state
                st.text_area("Extracted Text (Preprocessed)", contract_text, height=200)
                
            if st.button("Analyze Contract"):
                with st.spinner('Analyzing contract...', show_time=True):
                    analysis_result = pdf_handler.analyze_contract(
                        st.session_state.contract_text,
                        language.lower()
                    )
                    st.session_state.analysis_result = analysis_result  # Save result to session state
                    st.success("Contract analyzed!")
    
    else:  # Paste Text option
        contract_text = st.text_area(
            "Paste your contract text here:",
            height=300,
            help="Text will be preprocessed to optimize token usage",
            value=st.session_state.contract_text  # Use session state for text
        )
        
        if st.button("Analyze Text"):
            with st.spinner('Analyzing text...', show_time=True):
                analysis_result = pdf_handler.analyze_contract(
                    contract_text,
                    language.lower()
                )
                st.session_state.analysis_result = analysis_result  # Save result to session state
                st.success("Text analyzed!")
    
    # Display results
    if st.session_state.analysis_result:
        st.markdown("### Analysis Results")  # Use st.markdown for the header
        st.markdown(st.session_state.analysis_result)  # Render result as Markdown
        
        # Show token usage warning if text is long
        if st.session_state.contract_text and len(st.session_state.contract_text) > 100000:
            st.warning("⚠️ Long text detected. Analysis was performed on first portion to optimize costs.")
        
        # Add "Clear Contract" button under analysis results
        if st.button("Clear Contract"):
            # Clear session state and cache
            st.session_state.uploaded_file = None
            st.session_state.contract_text = ""
            st.session_state.analysis_result = None
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()  # Rerun the app to reset the UI
            st.success("Contract and cache cleared successfully!")

if __name__ == "__main__":
    main()