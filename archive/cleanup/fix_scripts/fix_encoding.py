#!/usr/bin/env python3
"""Fix Unicode encoding issues in Python files"""

import sys

def remove_emojis(text):
    """Remove emoji characters from text"""
    result = []
    for char in text:
        code = ord(char)
        # Skip emojis and other non-ASCII chars
        if code > 127:
            continue
        result.append(char)
    return ''.join(result)

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    cleaned = remove_emojis(content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    
    print(f"Fixed: {filepath}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fix_file(sys.argv[1])
    else:
        # Fix common files
        for filepath in ['migrate_to_cloud.py', 'kuera_setup_database.py']:
            try:
                fix_file(filepath)
            except Exception as e:
                print(f"Error with {filepath}: {e}")
