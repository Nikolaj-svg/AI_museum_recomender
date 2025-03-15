import chromadb
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import os

# Инициализация базы ChromaDB
db = chromadb.PersistentClient(path="data/chroma_db")

# Создаём коллекцию для хранения данных
collection = db.get_or_create_collection(name="museum_data")

def add_document(text: str, source: str):
    """Добавляет документ в базу"""
    collection.add(
        documents=[text], 
        metadatas=[{"source": source}], 
        ids=[str(hash(text))]
    )

def search_documents(query: str, top_k: int = 3):
    """Поиск информации по запросу"""
    results = collection.query(query_texts=[query], n_results=top_k)
    return results["documents"]
