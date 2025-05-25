#!/usr/bin/env python3

import os
from dataclasses import dataclass
from config import pdf_size_token_limit
from functools import cache
from typing import Any, BinaryIO, Dict, List, Optional, Tuple
from config import vector_db_config

import pypdf


@dataclass
class Document:
    document: str
    page: int
    text: str
    id: str


def cache_result(func):
    """
    A decorator that caches the results of a function call.

    Args:
        func: The function to be decorated

    Returns:
        A wrapper function that caches results
    """
    cache = {}

    def wrapper(*args, **kwargs):
        # Create a hashable key from the arguments
        key = str(args) + str(sorted(kwargs.items()))

        # Return cached result if available
        if key in cache:
            return cache[key]

        # Calculate result and store in cache
        result = func(*args, **kwargs)
        cache[key] = result
        return result

    return wrapper


@cache_result
def extract_pdf_text_by_page(filename: str) -> List[Document]:
    """Extract text from a single PDF file and return as page chunks

    :param filename: Path to PDF file
    :return: List of Document objects with metadata
    """
    if not (os.path.exists(filename) and filename.lower().endswith(".pdf")):
        return []

    with open(filename, "rb") as f:
        reader = pypdf.PdfReader(f)
        base_name = os.path.basename(filename)

        return [
            Document(
                document=base_name,
                page=i + 1,
                text=page.extract_text(),
                id=f"{base_name}_page_{i+1}",
            )
            for i, page in enumerate(reader.pages)
            if page.extract_text().strip()
        ]


def extract_chunks_from_txt(file_path, chunk_size=vector_db_config["chunk_size"]):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks


@cache_result
def process_file(file_path: str) -> List[Document]:
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".pdf":
        print("Processing PDF file...")
        documents = extract_pdf_text_by_page(file_path)
    elif ext == ".txt":
        print("Processing TXT file...")
        documents = extract_chunks_from_txt(
            file_path, chunk_size=vector_db_config["chunk_size"]
        )
    else:
        raise ValueError("Unsupported file type. Please provide a PDF or TXT file.")

    return documents


def extract_text(documents: List[Document]) -> str:
    return "\n".join(documents.text)


def create_context(files: List[str]) -> str:
    context = None
    if files and len(files) > 0:
        texts = []
        text_per_file = round(pdf_size_token_limit / len(files))
        for f in files:
            f_doc = process_file(f)
            f_text = extract_text(f_doc)
            f_text = f_text[:text_per_file]
            texts.append(f_text)

        pdf_text = "\n".join(texts)

        context = f"Use this information to answer questions:\n{pdf_text}"
    return context
