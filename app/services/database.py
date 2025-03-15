import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
db = chromadb.PersistentClient(path="data/chroma_db")
collection = db.get_or_create_collection(name="museum_data")

def save_artwork(title, description, museum):
    """Сохраняет картину в базе"""
    embedding = model.encode(description).tolist()
    collection.add(
        documents=[description],
        metadatas=[{"title": title, "museum": museum}],
        embeddings=[embedding],
        ids=[title]
    )

def search_artwork(query, top_k=3):
    """Поиск по базе"""
    query_embedding = model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return results["documents"]
