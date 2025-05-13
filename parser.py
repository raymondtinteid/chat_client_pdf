#!/usr/bin/env python3

import os
import PyPDF2
from typing import List, Dict, Any, BinaryIO, Optional, Tuple
from dataclasses import dataclass
from functools import cache


@dataclass
class Document:
    document: str
    page: int
    text: str


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
def extract_pdf_text_by_page(filenames: List[str]) -> List[Document]:
    """Extract text from multiple PDF files and return as page chunks
    
    :param filenames: List of PDF file paths
    :type filenames: List[str]
    :return: List of Document objects, each containing document name, page number, and extracted text.
    :rtype: List[Document]
    """
    chunks: List[Document] = []
    for filename in filenames:
        if os.path.exists(filename) and filename.lower().endswith('.pdf'):
            with open(filename, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:  # Skip empty pages
                        chunks.append(
                            Document(
                                document=os.path.basename(filename),
                                page=i + 1,
                                text=text,
                            )
                        )
    return chunks
