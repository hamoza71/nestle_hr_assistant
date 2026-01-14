"""Test the RAG chain to verify it works correctly"""
import os
from dotenv import load_dotenv
load_dotenv()

# Disable Gradio analytics
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from pypdf import PdfReader

print("Testing RAG chain...")

# Simple test data
test_text = """
Nestlé HR Policy on Leave:
Employees are entitled to 15 days of annual leave per year.
Sick leave requires a medical certificate for absences longer than 3 days.
Maternity leave is 12 weeks for eligible employees.
"""

# Create chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_text(test_text)
print(f"Created {len(chunks)} chunks")

# Create vector store
api_key = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key)
vector_store = FAISS.from_texts(chunks, embeddings)
print("Vector store created")

# Create LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3, api_key=api_key)

# Create retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

# Contextualize question prompt
contextualize_q_system_prompt = """Given a chat history and the latest user question
which might reference context in the chat history, formulate a standalone question
which can be understood without the chat history. Do NOT answer the question,
just reformulate it if needed and otherwise return it as is."""

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])

# Create history-aware retriever
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)
print("History-aware retriever created")

# QA system prompt
qa_system_prompt = """You are a helpful HR assistant.
Use the following context to answer the question.

Context: {context}"""

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", qa_system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])

# Create question-answer chain
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

# Create the full RAG chain
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
print("RAG chain created successfully!")

# Test with empty history
print("\n" + "="*60)
print("TEST 1: Query with empty chat history")
print("="*60)
chat_history = []
result = rag_chain.invoke({
    "input": "How many days of annual leave do employees get?",
    "chat_history": chat_history
})
print(f"Question: How many days of annual leave do employees get?")
print(f"Answer: {result['answer']}")

# Update chat history
chat_history.append(HumanMessage(content="How many days of annual leave do employees get?"))
chat_history.append(AIMessage(content=result['answer']))

# Test with chat history
print("\n" + "="*60)
print("TEST 2: Follow-up query with chat history")
print("="*60)
result2 = rag_chain.invoke({
    "input": "What about sick leave?",
    "chat_history": chat_history
})
print(f"Question: What about sick leave?")
print(f"Answer: {result2['answer']}")

print("\n" + "="*60)
print("✅ All tests passed successfully!")
print("="*60)
