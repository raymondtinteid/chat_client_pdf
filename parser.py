#!/usr/bin/env python3

import os
import PyPDF2
import pandas as pd
from sentence_transformers import SentenceTransformer


def extract_pdf_text_by_page(files):
    """Extract text from multiple PDF files and return as page chunks"""
    chunks = []
    for file in files:
        with open(file.name, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:  # Skip empty pages
                    chunks.append(
                        {
                            "document": os.path.basename(file.name),
                            "page": i + 1,
                            "text": text,
                        }
                    )
    return chunks


def create_embeddings(chunks, model_name="all-MiniLM-L6-v2"):
    """Create embeddings for each text chunk"""
    model = SentenceTransformer(model_name)

    # Extract just the text from each chunk for embedding
    texts = [chunk["text"] for chunk in chunks]

    # Generate embeddings
    embeddings = model.encode(texts)

    # Add embeddings to the chunks
    for i, chunk in enumerate(chunks):
        chunk["embedding"] = embeddings[i]

    return chunks


def save_embeddings_to_parquet(chunks, output_file="embeddings.parquet"):
    """Save chunks with embeddings to a Parquet file"""
    # Convert chunks to a DataFrame
    df = pd.DataFrame(chunks)

    # Save as Parquet
    df.to_parquet(output_file)
    print(f"Embeddings saved to {output_file}")
    return output_file


def load_embeddings_from_parquet(file_path="embeddings.parquet"):
    """Load embeddings from a Parquet file"""
    df = pd.read_parquet(file_path)
    return df.to_dict("records")


def process_pdfs(files, output_file="embeddings.parquet"):
    """Process PDF files: extract text, create embeddings, and save to file"""
    # Extract text by page
    chunks = extract_pdf_text_by_page(files)

    # Create embeddings
    chunks_with_embeddings = create_embeddings(chunks)

    # Save to file
    save_embeddings_to_parquet(chunks_with_embeddings, output_file)

    return chunks_with_embeddings
