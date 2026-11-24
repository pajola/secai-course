from pathlib import Path

import chromadb
import ollama

from nora.config import EMBED_MODEL

DOCS = Path("data/docs")
collection = chromadb.PersistentClient(path=".chroma").get_or_create_collection("nora")


def embed(texts: list[str]) -> list[list[float]]:
    return ollama.embed(model=EMBED_MODEL, input=texts)["embeddings"]


def ingest() -> None:
    files = sorted(DOCS.glob("*/*.md"))
    texts = [f.read_text() for f in files]
    collection.upsert(
        ids=[str(f.relative_to(DOCS)) for f in files],
        documents=texts,
        embeddings=embed(texts),
        # the folder name is the document's classification label
        metadatas=[{"classification": f.parent.name, "source": str(f.relative_to(DOCS))} for f in files],
    )
    print(f"Ingested {len(files)} documents")


def retrieve(query: str, k: int = 3, where: dict | None = None) -> list[dict]:
    result = collection.query(query_embeddings=embed([query]), n_results=k, where=where)
    return [
        {"text": text, **meta}
        for text, meta in zip(result["documents"][0], result["metadatas"][0])
    ]


if __name__ == "__main__":
    ingest()
