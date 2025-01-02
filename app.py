import gradio as gr
import anthropic
import os
from typing import List, Tuple

# Check for API key and initialize the Anthropic client
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("Please set the ANTHROPIC_API_KEY environment variable")

# Initialize the Anthropic client with the correct syntax
client = Anthropic(api_key=api_key)


# Custom system prompt for contract analysis
SYSTEM_PROMPT = """Hola, quiero que me ayudes a evaluar un contrato y determinar si es favorable para mi o si tengo alguna desventaja. Una vez cargado el contrato, por favor necesito que:

1. Identificar el propósito principal del contrato.
2. Determinar las principales obligaciones y responsabilidades asignadas al usuario.
3. Evaluar los potenciales riesgos y desventajas para el usuario.
4. Analizar las cifras del contrato (por ejemplo, montos de pagos, plazos, penalizaciones, etc.) y determinar si son razonables y favorables para el usuario.
5. Revisar las cláusulas de terminación y rescisión del contrato, incluyendo cualquier penalización por incumplimiento.
6. Evaluar las cláusulas de confidencialidad y no competencia, si aplican.
7. Verificar la claridad y comprensión de los términos y condiciones del contrato.
8. Identificar cualquier cláusula que pueda ser desfavorable para el usuario, como cláusulas de arbitraje obligatorio o limitaciones de responsabilidad.
9. Proporcionar recomendaciones sobre la legislación del país de jurisdicción del contrato, incluyendo cualquier requisito legal específico que deba cumplirse.
10. Proporcionar una recomendación sobre si el contrato es favorable o no.

Quiero que hagas especial énfasis en la propiedad intelectual y compensaciones y presenta todas las obersavciones en Ideas principales y bullepoints en un formato Markdown

No es necesario que repitas las instrucciones, solo por favor confírmame si has comprendido todos los puntos para que pueda subir el contrato."""

def analyze_contract(message: str, history: List[Tuple[str, str]]) -> str:
    """
    Process the contract text and return analysis using Claude API
    """
    try:
        # Construct messages including chat history
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]
        
        # Add chat history
        for human_msg, assistant_msg in history:
            messages.extend([
                {"role": "user", "content": human_msg},
                {"role": "assistant", "content": assistant_msg}
            ])
            
        # Add current message
        messages.append({"role": "user", "content": message})

        # Get response from Claude
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            messages=messages
        )
        
        return response.content[0].text

    except Exception as e:
        return f"An error occurred: {str(e)}"

# Create the Gradio interface
def create_interface():
    with gr.Blocks(css="footer {display: none}") as interface:
        gr.Markdown("# Contract Analysis Assistant")
        gr.Markdown("""
        Upload contract text or ask questions about previously uploaded contracts.
        The assistant will analyze key terms, risks, and important clauses.
        """)
        
        chatbot = gr.Chatbot(
            height=400,
            show_label=False,
        )
        
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Enter contract text or ask a question...",
                show_label=False,
                container=False,
            )
            submit = gr.Button("Send", variant="primary")

        gr.Examples(
            examples=[
                "Can you analyze this employment agreement for any red flags?",
                "What are the key terms in this software license agreement?",
                "Please review the termination clauses in this contract.",
            ],
            inputs=msg,
        )

        msg.submit(
            analyze_contract,
            [msg, chatbot],
            [chatbot],
            queue=False
        )
        
        submit.click(
            analyze_contract,
            [msg, chatbot],
            [chatbot],
            queue=False
        )
        
        # Clear button
        clear = gr.Button("Clear Conversation")
        clear.click(lambda: None, None, chatbot, queue=False)

    return interface

if __name__ == "__main__":
    # Create and launch the interface
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
    )