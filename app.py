"""
Nestlé HR Assistant - RAG-based Chatbot
A conversational AI assistant for HR policies using Retrieval Augmented Generation
"""

import os
from dotenv import load_dotenv
import gradio as gr
from pypdf import PdfReader
import numpy as np
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = None

# ============================================================================
# CONFIGURATION
# ============================================================================

PDF_PATH = "Nestle_hr_policy_pdf_2012.pdf"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.3
TOP_K_RESULTS = 4

# ============================================================================
# PDF PROCESSING
# ============================================================================

def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n\n"
    return text

def create_text_chunks(text):
    """Split text into overlapping chunks for better retrieval."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end - CHUNK_OVERLAP
    return chunks

# ============================================================================
# VECTOR STORE
# ============================================================================

class SimpleVectorStore:
    """A simple vector store using numpy for similarity search."""
    
    def __init__(self):
        self.chunks = []
        self.embeddings = []
    
    def add_texts(self, texts, embeddings):
        """Add texts and their embeddings to the store."""
        self.chunks.extend(texts)
        self.embeddings.extend(embeddings)
    
    def similarity_search(self, query_embedding, k=4):
        """Find the k most similar chunks to the query."""
        if not self.embeddings:
            return []
        
        query_vec = np.array(query_embedding)
        doc_vecs = np.array(self.embeddings)
        
        # Cosine similarity
        query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
        doc_norms = doc_vecs / (np.linalg.norm(doc_vecs, axis=1, keepdims=True) + 1e-10)
        similarities = np.dot(doc_norms, query_norm)
        
        top_indices = np.argsort(similarities)[-k:][::-1]
        return [self.chunks[i] for i in top_indices]

# ============================================================================
# EMBEDDINGS & RAG
# ============================================================================

def get_embedding(text):
    """Get embedding for a text using OpenAI."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

def get_embeddings_batch(texts):
    """Get embeddings for multiple texts."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [item.embedding for item in response.data]

def create_vector_store(chunks):
    """Create vector store from text chunks."""
    store = SimpleVectorStore()
    
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        embeddings = get_embeddings_batch(batch)
        store.add_texts(batch, embeddings)
    
    return store

def get_relevant_context(query, vector_store, k=TOP_K_RESULTS):
    """Retrieve relevant context for a query."""
    query_embedding = get_embedding(query)
    relevant_chunks = vector_store.similarity_search(query_embedding, k=k)
    return "\n\n---\n\n".join(relevant_chunks)

# ============================================================================
# RESPONSE GENERATION
# ============================================================================

SYSTEM_PROMPT = """You are the Nestlé HR Assistant, a helpful and professional AI assistant 
specialized in answering questions about Nestlé's Human Resources policies and procedures.

Use the following context from Nestlé HR policy documents to answer the question. 
If you don't find the answer in the context, politely say that you don't have that specific 
information in the HR policy documents and suggest contacting the HR department directly.

Always be:
- Professional and courteous
- Clear and concise in your responses
- Accurate to the policy documents
- Helpful in guiding employees to the right resources

Context from HR Documents:
{context}"""

def extract_message_text(content):
    """Extract plain text from Gradio 6.x content format."""
    if isinstance(content, str):
        return content
    if isinstance(content, list) and len(content) > 0:
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                return part.get("text", "")
            if isinstance(part, str):
                return part
    return str(content) if content else ""

def generate_response(query, context, chat_history):
    """Generate a response using the LLM with context."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(context=context)}
    ]

    # Add chat history (extract text from Gradio 6.x format)
    for msg in chat_history:
        role = msg.get("role")
        content = extract_message_text(msg.get("content", ""))
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    # Add current query
    messages.append({"role": "user", "content": query})

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=TEMPERATURE
    )

    return response.choices[0].message.content or ""

def generate_response_streaming(query, context, chat_history):
    """Generate a streaming response using the LLM with context."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(context=context)}
    ]

    # Add chat history (extract text from Gradio 6.x format)
    for msg in chat_history:
        role = msg.get("role")
        content = extract_message_text(msg.get("content", ""))
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    # Add current query
    messages.append({"role": "user", "content": query})

    stream = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        stream=True
    )

    response_text = ""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            response_text += chunk.choices[0].delta.content
            yield response_text

# ============================================================================
# INITIALIZE SYSTEM
# ============================================================================

def initialize_system():
    """Initialize the RAG system with the PDF document."""
    global client
    
    print("🔄 Initializing Nestlé HR Assistant...")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found! Please create a .env file with your API key.")
    
    client = OpenAI(api_key=api_key)
    
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF file not found: {PDF_PATH}")
    
    print("📄 Extracting text from PDF...")
    text = extract_text_from_pdf(PDF_PATH)
    print(f"   Extracted {len(text)} characters")
    
    print("✂️  Creating text chunks...")
    chunks = create_text_chunks(text)
    print(f"   Created {len(chunks)} chunks")
    
    print("🔢 Creating embeddings and vector store...")
    vector_store = create_vector_store(chunks)
    print("   Vector store ready")
    
    print("✅ System initialized successfully!")
    
    return vector_store

# ============================================================================
# GRADIO INTERFACE (Using Gradio 6.x dict format)
# ============================================================================

def create_chat_interface(vector_store):
    """Create the Gradio chat interface."""
    
    def user_input(message, history):
        """Handle user input - add to history immediately."""
        if not message.strip():
            return "", history
        # Gradio 6.x dict format: {"role": "user/assistant", "content": "..."}
        return "", history + [{"role": "user", "content": message}]
    
    def bot_response(history):
        """Generate bot response with streaming."""
        # Check if history is empty or last message is not from user
        if not history or history[-1].get("role") != "user":
            yield history
            return

        # Extract text from Gradio 6.x content format
        user_message = extract_message_text(history[-1].get("content", ""))

        try:
            context = get_relevant_context(user_message, vector_store)

            # Add empty assistant message for streaming
            history = history + [{"role": "assistant", "content": ""}]

            # Stream the response
            for partial in generate_response_streaming(user_message, context, history[:-2]):
                history[-1]["content"] = partial
                yield history

        except Exception as e:
            error_msg = f"I apologize, but I encountered an error. Please try again. Error: {str(e)}"
            if history and history[-1].get("role") == "assistant":
                history[-1]["content"] = error_msg
            else:
                history = history + [{"role": "assistant", "content": error_msg}]
            yield history
    
    def clear_chat():
        return [], ""
    
    # Build interface with basic Gradio components
    with gr.Blocks(title="Nestlé HR Assistant") as demo:
        
        gr.Markdown("""
        # 🏢 Nestlé HR Assistant
        *Good Food, Good Life*
        
        Ask me anything about Nestlé's HR policies and procedures!
        """)
        
        chatbot = gr.Chatbot(
            value=[],
            height=450,
            show_label=False,
            # Gradio 6.x uses dict format: [{"role": "user/assistant", "content": "..."}]
        )
        
        with gr.Row():
            msg_input = gr.Textbox(
                placeholder="Ask about HR policies, benefits, or procedures...",
                show_label=False,
                scale=9,
            )
            send_btn = gr.Button("Send", variant="primary", scale=1)
        
        with gr.Row():
            clear_btn = gr.Button("🗑️ Clear Chat")
        
        gr.Markdown("""
        ---
        *Powered by GPT-4o-mini | For internal use only | Information may not be 100% accurate*
        """)
        
        # Event handlers with chaining
        msg_input.submit(
            user_input,
            [msg_input, chatbot],
            [msg_input, chatbot],
            queue=False
        ).then(
            bot_response,
            chatbot,
            chatbot
        )
        
        send_btn.click(
            user_input,
            [msg_input, chatbot],
            [msg_input, chatbot],
            queue=False
        ).then(
            bot_response,
            chatbot,
            chatbot
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[chatbot, msg_input]
        )
    
    return demo

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 60)
    print("   🏢 NESTLÉ HR ASSISTANT - RAG CHATBOT")
    print("=" * 60)
    
    # Disable Gradio analytics (avoids network errors)
    os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
    
    try:
        vector_store = initialize_system()
        
        print("\n🚀 Launching Gradio interface...")
        demo = create_chat_interface(vector_store)
        demo.launch(
            server_name="127.0.0.1",  # localhost only
            server_port=7860,
            share=False,
            show_error=True
        )
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("   Please ensure the PDF file is in the same directory.")
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("   Please create a .env file with your OpenAI API key:")
        print("   OPENAI_API_KEY=sk-your-api-key-here")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise

if __name__ == "__main__":
    main()
