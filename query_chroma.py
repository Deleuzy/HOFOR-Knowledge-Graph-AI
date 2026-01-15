#!/usr/bin/env python3
"""
Query the Chroma DB and optionally generate a RAG answer via OpenAI.
"""
import os
import sys
from sentence_transformers import SentenceTransformer
import chromadb
import openai

CHROMA_DIR = "./storage/chroma_db"
EMBED_MODEL = "all-MiniLM-L6-v2"
N_RESULTS = 5
LLM_MODEL = "gpt-4"

def rag_query(query_text: str, use_llm: bool = True):
    embedder = SentenceTransformer(EMBED_MODEL)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(name="industrial_automation_kb")

    q_emb = embedder.encode(query_text).tolist()
    results = collection.query(query_embeddings=[q_emb], n_results=N_RESULTS)

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    print(f"Top {len(docs)} matches:")
    context = []
    for i, (d, m) in enumerate(zip(docs, metas), 1):
        print(f"\n[{i}] source={m.get('source')} id={m.get('chunk_id')}\n{d[:1000]}\n---")
        context.append(f"Source: {m.get('source')} \n{d}")

    if not use_llm:
        return docs, metas

    prompt = (
        "You are an industrial automation expert. Use the following context from past projects to answer the user query.\n\n"
        "CONTEXT:\n"
        f"{''.join(context[:5])}\n\n"
        "QUESTION:\n"
        f"{query_text}\n\n"
        "Provide: 1) Risk assessment, 2) Recommended hardware/software, 3) Time estimate with justification, "
        "4) Key issues and suggested fixes. Reference the context where relevant."
    )

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("OPENAI_API_KEY not set; returning retrieved documents only.")
        return docs, metas

    openai.api_key = openai_api_key
    resp = openai.ChatCompletion.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1000
    )
    answer = resp.choices[0].message.content
    print("\n=== RAG Answer from LLM ===\n")
    print(answer)
    return docs, metas, answer

if __name__ == "__main__":
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
    else:
        q = input("Enter query: ")
    rag_query(q, use_llm=True)

