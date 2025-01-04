import streamlit as st
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
    st.write('##### Made with love by Johnometalman')
    st.divider()
    
    # Sidebar for configurations
    st.sidebar.header("Configuration.. if you want")
    
    # Model selection
    model_option = st.sidebar.selectbox(
        "Select Model (Cost: Low → High)",
        [
            "claude-3-haiku-20240307 (Fastest, Lowest Cost)",
            "claude-3-sonnet-20240229 (Balanced)",
            "claude-3-opus-20240229 (Most Detailed)"
        ],
        index=0
    )
    
    # Extract model name from selection
    model_name = model_option.split(" ")[0]
    
    # Token limit selection
    max_tokens = st.sidebar.slider(
        "Max Response Tokens (Higher = More Detailed, More Cost)",
        min_value=250,
        max_value=4096,
        value=1000,
        step=250
    )
    
    # Initialize PDFHandler with selected configuration
    pdf_handler = PDFHandler(model_name=model_name, max_tokens=max_tokens)
    
    # Main content
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
    
    # Cost estimation disclaimer
    st.sidebar.markdown("""
    ### Approximate Cost Guide
    - Haiku: Lowest cost (≈1/10 of Opus)
    - Sonnet: Medium cost (≈1/2 of Opus)
    - Opus: Highest cost
    
    """)
    
    analysis_result = None
    
    if input_method == "Upload PDF":
        uploaded_file = st.file_uploader("Upload your contract (PDF)", type=['pdf'])
        
        if uploaded_file is not None:
            with st.spinner('Extracting and preprocessing text...'):
                contract_text = pdf_handler.extract_text_from_pdf(uploaded_file)
                st.text_area("Extracted Text (Preprocessed)", contract_text, height=200)
                
            if st.button("Analyze Contract"):
                with st.spinner('Analyzing contract...'):
                    analysis_result = pdf_handler.analyze_contract(
                        contract_text,
                        language.lower()
                    )
    
    else:  # Paste Text option
        contract_text = st.text_area(
            "Paste your contract text here:",
            height=300,
            help="Text will be preprocessed to optimize token usage"
        )
        
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
        
        # Show token usage warning if text is long
        if len(contract_text) > 10000:
            st.warning("⚠️ Long text detected. Analysis was performed on first portion to optimize costs.")

if __name__ == "__main__":
    main()