#!/usr/bin/env python3
"""
Standalone PDF extractor - dipanggil via subprocess
"""

import sys
import json

def extract_pdf(file_path):
    """Extract text dari PDF"""
    try:
        import PyPDF2
        text = []
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return '\n\n'.join(text)
    except Exception as e:
        return f"[Error extracting PDF: {str(e)}]"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <pdf_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    text = extract_pdf(file_path)
    print(json.dumps({'text': text}))
