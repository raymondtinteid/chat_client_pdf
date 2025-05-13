#!/usr/bin/env python3

import os
import PyPDF2
from typing import List, Dict, Any, BinaryIO, Optional
from dataclasses import dataclass


@dataclass
class Document:
    document: str
    page: int
    text: str


def extract_pdf_text_by_page(files: List[BinaryIO]) -> List[Document]:
    """Extract text from multiple PDF files and return as page chunks

    :param files: List of file-like objects representing PDF files.
    :type files: List[BinaryIO]
    :return: List of Document objects, each containing document name, page number, and extracted text.
    :rtype: List[Document]
    """
    chunks: List[Document] = []
    for file in files:
        with open(file.name, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:  # Skip empty pages
                    chunks.append(
                        Document(
                            document=os.path.basename(file.name),
                            page=i + 1,
                            text=text,
                        )
                    )
    return chunks
