#!/usr/bin/env python3

import os
import PyPDF2
import pandas as pd


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
