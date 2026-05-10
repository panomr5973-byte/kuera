#!/usr/bin/env python3
"""
Standalone DOCX extractor - dipanggil via subprocess
"""

import sys
import json

# Add user site-packages to path
sys.path.insert(0, r'C:\Users\Admin\AppData\Roaming\Python\Python314\site-packages')

def extract_docx(file_path):
    """Extract text dari DOCX"""
    try:
        import docx
        doc = docx.Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return '\n\n'.join(paragraphs)
    except Exception as e:
        return f"[Error extracting DOCX: {str(e)}]"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python docx_extractor.py <docx_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    text = extract_docx(file_path)
    print(json.dumps({'text': text}))
