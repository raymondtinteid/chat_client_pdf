import os
from functools import reduce
from typing import List

import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

from config import model_config, vector_db_config
from pdfparser import Document, extract_pdf_text_by_page


if model_config["text-embedding-3-large"]["azure_endpoint"]:
    embedding = model_config["text-embedding-3-large"]

    embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        api_key=embedding["api_key"],
        api_base=embedding["azure_endpoint"],
        api_type="azure",
        api_version=embedding["api_version"],
        model_name=embedding["api_model"],
    )
else:
    embedding_function = embedding_functions.DefaultEmbeddingFunction()


client = chromadb.Client()

collection = client.get_or_create_collection(
    name="my_collection", embedding_function=embedding_function
)


def add_document(collection, document: Document):
    existing = collection.get(ids=[document.id])
    if document.id not in existing["ids"]:
        # ID already exists, skip adding
        collection.add(
            documents=[document.text],
            ids=[document.id],
            metadatas=[{"page": document.page}],
        )
    return collection


def embed_documents_to_chroma(
    documents: List[Document],
    collection_name=vector_db_config["chroma_db_collection"],
    chroma_path=vector_db_config["chroma_db_path"],
):
    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_or_create_collection(
        name=collection_name, embedding_function=embedding_function
    )

    reduce(
        lambda col, doc: add_document(col, doc),
        documents,
        collection,
    )


if __name__ == "__main__":
    file_path = "test_sample.pdf"  # Replace with your PDF or TXT file path
    documents = process_file(file_path)
    chroma_path = "./chroma_db"
    embed_documents_to_chroma(documents, chroma_path=chroma_path)
