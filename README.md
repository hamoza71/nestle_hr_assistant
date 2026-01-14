# 🏢 Nestlé HR Assistant

A conversational AI chatbot powered by RAG (Retrieval Augmented Generation) for answering HR policy questions using Nestlé's HR Policy documents.

## 🎯 Features

- **PDF-based Knowledge**: Extracts and indexes Nestlé HR policy documents
- **Semantic Search**: Uses FAISS vector store for efficient retrieval
- **Conversational AI**: Maintains context across the conversation
- **Professional UI**: Matches Nestlé's corporate design language
- **In-session Memory**: Remembers previous questions in the chat

## 🏗️ Architecture

```
PDF Document → Text Extraction → Chunking → Embeddings → Vector Store
                                                              ↓
User Query → History-Aware Retriever → Context Retrieval → GPT → Response
```

## 📋 Prerequisites

- Python 3.9 or higher
- OpenAI API key

## 🚀 Quick Start

### 1. Navigate to Project Directory

```bash
cd nestle_hr_assistant
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create .env File

Copy the example file and add your API key:

```bash
cp .env.example .env
```

Then edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 5. Run the Application

```bash
python app.py
```

### 6. Open in Browser

Navigate to: `http://localhost:7860`

## 📁 Project Structure

```
nestle_hr_assistant/
├── app.py                          # Main application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .env                            # Your API key (create this)
├── Nestle_hr_policy_pdf_2012.pdf  # HR Policy document
└── README.md                       # This file
```

## 🔧 Configuration

You can modify these settings in `app.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `CHUNK_SIZE` | 500 | Size of text chunks for indexing |
| `CHUNK_OVERLAP` | 50 | Overlap between chunks |
| `LLM_MODEL` | gpt-3.5-turbo | OpenAI model to use |
| `TEMPERATURE` | 0.3 | Response creativity (0-1) |
| `TOP_K_RESULTS` | 4 | Number of chunks to retrieve |

## 💬 Example Questions

- "What is the policy on parental leave?"
- "How does Nestlé handle employee training?"
- "What are the Total Rewards at Nestlé?"
- "Tell me about the hiring process"
- "What is Nestlé's approach to employee relations?"

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| UI Framework | Gradio |
| LLM | OpenAI GPT-3.5/4 |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Store | FAISS |
| PDF Processing | pypdf |
| Orchestration | LangChain |

## ⚠️ Troubleshooting

### "OPENAI_API_KEY not found"
Make sure you've created a `.env` file with your API key.

### "PDF file not found"
Ensure `Nestle_hr_policy_pdf_2012.pdf` is in the same directory as `app.py`.

### Import errors
Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt --upgrade
```

### Slow first response
The first query takes longer as it initializes embeddings. Subsequent queries are faster.

## 📄 License

This project is for educational/demonstration purposes. Nestlé branding and documents are property of Nestlé S.A.

---

Built with ❤️ using Python, LangChain, and Gradio
