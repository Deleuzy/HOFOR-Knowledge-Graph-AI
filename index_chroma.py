#!/usr/bin/env python3
"""
Index PDFs into a ChromaDB collection using local sentence-transformers embeddings.
Run once to build the database; re-run when new PDFs are added.
"""
import glob
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from src.document_parser import IndustrialAutomationParser

# Configuration
DOCS_DIR = "/Users/bogdanandone/Desktop/Optimization/svsamletopgavebeskrivelse/data"
CHROMA_DIR = "./storage/chroma_db"
EMBED_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def chunk_text(text: str, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    if not text:
        return []
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(start + size, L)
        chunks.append(text[start:end])
        start = end - overlap if end - overlap > start else end
    return chunks

def main():
    parser = IndustrialAutomationParser()
    embedder = SentenceTransformer(EMBED_MODEL)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(name="industrial_automation_kb")

    pdf_files = [p for p in glob.glob(os.path.join(DOCS_DIR, "*.pdf"))]
    print(f"Indexing {len(pdf_files)} PDF(s)...")

    for pdf_path in pdf_files:
        try:
            print("→", pdf_path)
            text = parser.extract_text_from_pdf(pdf_path)
            chunks = chunk_text(text)
            basename = Path(pdf_path).stem
            for i, chunk in enumerate(chunks):
                emb = embedder.encode(chunk).tolist()
                doc_id = f"{basename}_chunk_{i}"
                metadata = {"source": basename, "chunk_id": doc_id}
                collection.add(
                    embeddings=[emb],
                    documents=[chunk],
                    metadatas=[metadata],
                    ids=[doc_id]
                )
        except Exception as e:
            print(f"Error indexing {pdf_path}: {e}")

    print("Indexing complete. Chroma DB stored at", CHROMA_DIR)

if __name__ == "__main__":
    main()

