#!/usr/bin/env python
with open('kuera_web_server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and fix line 227 (0-indexed: 226)
for i, line in enumerate(lines):
    if 'filename, content, summary, keywords = result' in line and 'file_type' not in line:
        lines[i] = line.replace('filename, content, summary, keywords = result',
                                 'filename, content, summary, keywords, file_type = result')
        print(f"Fixed line {i+1}")
    
    # Fix return statements
    if 'summary[:800]' in line:
        lines[i] = line.replace('summary[:800]', 'summary[:1200]')
        print(f"Fixed summary line {i+1}")
    
    if 'content[:800]' in line and 'Isi Dokumen' in lines[i-1] if i > 0 else False:
        # Replace the entire elif block
        lines[i] = '''                        preview = content[:2500] if len(content) > 2500 else content
                        return f"📄 **{filename}**\\n\\n📝 **Isi Dokumen:**\\n{preview}\\n\\n... (Total: {len(content):,} karakter)"
                    elif summary and len(summary) > 50:
                        return f"📄 **{filename}**\\n\\n📝 **Ringkasan:**\\n{summary[:1200]}"
'''
        print(f"Fixed content line {i+1}")
        # Remove the next line since we combined them
        if i+1 < len(lines) and 'elif content:' in lines[i+1]:
            lines[i+1] = ''

with open('kuera_web_server.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Done!")
