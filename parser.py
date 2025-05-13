#!/usr/bin/env python3

import os
import PyPDF2
import pandas as pd
from typing import List, Dict, Any, BinaryIO


def extract_pdf_text_by_page(files: List[BinaryIO]) -> List[Dict[str, Any]]:
    """Extract text from multiple PDF files and return as page chunks

    :param files: List of file-like objects representing PDF files.
    :type files: List[BinaryIO]
    :return: List of dictionaries, each containing document name, page number, and extracted text.
    :rtype: List[Dict[str, Any]]
    """
    chunks: List[Dict[str, Any]] = []
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
