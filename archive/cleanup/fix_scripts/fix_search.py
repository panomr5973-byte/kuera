#!/usr/bin/env python
with open('kuera_web_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Update the SELECT query
old_select = """                    SELECT original_name, content_text, summary, keywords
                    FROM uploaded_files"""
new_select = """                    SELECT original_name, content_text, summary, keywords, file_type
                    FROM uploaded_files"""
content = content.replace(old_select, new_select)

# Fix 2: Update result unpacking and return
old_result = """                    filename, content, summary, keywords = result
                    # Return summary if available, otherwise first part of content
                    if summary and len(summary) > 50:
                        return f"📄 **{filename}**\\n\\n📝 **Ringkasan:**\\n{summary[:800]}"
                    elif content:
                        return f"📄 **{filename}**\\n\\n📝 **Isi Dokumen:**\\n{content[:800]}..."""

new_result = """                    filename, content, summary, keywords, file_type = result
                    # Return full content preview (up to 2500 chars)
                    if content and len(content) > 100:
                        preview = content[:2500] if len(content) > 2500 else content
                        return f"📄 **{filename}**\\n\\n📝 **Isi Dokumen:**\\n{preview}\\n\\n... (Total: {len(content):,} karakter)"
                    elif summary and len(summary) > 50:
                        return f"📄 **{filename}**\\n\\n📝 **Ringkasan:**\\n{summary[:1200]}"""

content = content.replace(old_result, new_result)

with open('kuera_web_server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed!")
