"""Index the CSV and answer queries using retrieval-augmented generation."""

import argparse

import pandas as pd

from sentence_transformers import SentenceTransformer

import chromadb

from cost_tracker import tracked_chat



EMB_MODEL = "all-MiniLM-L6-v2"

INDEX_PATH = "data/rust_faq.index"



client = chromadb.PersistentClient(path=INDEX_PATH)

embedder = SentenceTransformer(EMB_MODEL)



def build_index(csv_path="data/rust_faq.csv"):

    df = pd.read_csv(csv_path)

    vectors = embedder.encode(df["answer"].tolist(), show_progress_bar=True)

    coll = client.get_or_create_collection("rust-faq")

    coll.add(documents=df["answer"].tolist(), embeddings=vectors, ids=df["id"].astype(str).tolist())

    print("Index built/updated ->", INDEX_PATH)



def answer(question: str, k: int = 3):

    q_vec = embedder.encode([question])[0]

    docs = client.get_collection("rust-faq").query([q_vec], n_results=k)

    context = "\n\n".join(docs["documents"][0])

    prompt = (

        "You are a Rust helper. Use the context below to answer.\n\n"

        f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"

    )

    return tracked_chat(prompt)



if __name__ == "__main__":

    ap = argparse.ArgumentParser()

    ap.add_argument("--question", type=str, help="Rust FAQ question")

    ap.add_argument("--index", action="store_true", help="Rebuild index")

    args = ap.parse_args()



    if args.index:

        build_index()

    elif args.question:

        print(answer(args.question))

    else:

        ap.print_help()

