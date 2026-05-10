#!/usr/bin/env python
with open('kuera_web_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Direct string replacement
old_code = '''                    filename, content, summary, keywords = result
                    # Return summary if available, otherwise first part of content
                    if summary and len(summary) > 50:
                        return f"📄 **{filename}**\\n\\n📝 **Ringkasan:**\\n{summary[:800]}"
                    elif content:
                        return f"📄 **{filename}**\\n\\n📝 **Isi Dokumen:**\\n{content[:800]}..."'''

new_code = '''                    filename, content, summary, keywords, file_type = result
                    # Return full content preview (up to 2500 chars)
                    if content and len(content) > 100:
                        preview = content[:2500] if len(content) > 2500 else content
                        return f"📄 **{filename}**\\n\\n📝 **Isi Dokumen:**\\n{preview}\\n\\n... (Total: {len(content):,} karakter)"
                    elif summary and len(summary) > 50:
                        return f"📄 **{filename}**\\n\\n📝 **Ringkasan:**\\n{summary[:1200]}"'''

if old_code in content:
    content = content.replace(old_code, new_code)
    print("Replacement successful!")
else:
    print("Pattern not found")
    # Debug: print surrounding context
    idx = content.find('filename, content, summary, keywords = result')
    if idx >= 0:
        print(f"Found at index {idx}")
        print(repr(content[idx:idx+300]))

with open('kuera_web_server.py', 'w', encoding='utf-8') as f:
    f.write(content)
