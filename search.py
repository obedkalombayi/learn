import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


INDEX_PATH = "data/knowledge_base.index"
DOCUMENTS_PATH = "data/documents.json"

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


# Charger le modèle
model = SentenceTransformer(MODEL_NAME)


# Charger FAISS
index = faiss.read_index(INDEX_PATH)


# Charger les documents
with open(DOCUMENTS_PATH, "r", encoding="utf-8") as f:
    documents = json.load(f)


def search(query, top_k=5):

    # Transformer la question en vecteur
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    query_embedding = query_embedding.astype("float32")

    # Recherche
    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx == -1:
            continue

        results.append({
            "score": float(score),
            "question": documents[idx]["question"],
            "answer": documents[idx]["answer"]
        })
    return results

"""
# TEST

while True:

    query = input("\nQuestion (ou 'quit') : ")

    if query.lower() == "quit":
        break

    results = search(query)

    print("\n" + "=" * 60)
    print("RÉSULTATS")
    print("=" * 60)

    for i, result in enumerate(results, start=1):

        print(f"\n--- Résultat {i} ---")
        print(f"Score : {result['score']:.4f}")
        print(result["document"]["text"])
"""