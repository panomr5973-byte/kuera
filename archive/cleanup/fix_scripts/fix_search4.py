#!/usr/bin/env python
with open('kuera_web_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check the exact bytes around the target
idx = content.find('filename, content, summary, keywords = result')
if idx >= 0:
    with open('debug.txt', 'w', encoding='utf-8') as f:
        f.write(content[idx:idx+400])
    print(f"Found at index {idx}, wrote debug.txt")
    
    # Now do the replacement more carefully
    # Just replace line by line
    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if 'filename, content, summary, keywords = result' in line and 'file_type' not in line:
            new_lines.append('                    filename, content, summary, keywords, file_type = result')
            print(f"Fixed line {i+1}")
        elif '# Return summary if available, otherwise first part of content' in line:
            new_lines.append('                    # Return full content preview (up to 2500 chars)')
            print(f"Fixed comment line {i+1}")
        elif 'if summary and len(summary) > 50:' in line:
            new_lines.append(line)
            i += 1
            # Replace the return line
            if i < len(lines):
                new_lines.append('                        return f"📄 **{filename}**\\n\\n📝 **Ringkasan:**\\n{summary[:1200]}"')
                print(f"Fixed summary return line {i+1}")
                i += 1
            continue
        elif 'elif content:' in line and i > 0 and 'Isi Dokumen' in lines[i+1] if i+1 < len(lines) else False:
            new_lines.append('                    if content and len(content) > 100:')
            print(f"Fixed elif content line {i+1}")
            i += 1
            # Replace return
            if i < len(lines):
                new_lines.append('                        preview = content[:2500] if len(content) > 2500 else content')
                new_lines.append('                        return f"📄 **{filename}**\\n\\n📝 **Isi Dokumen:**\\n{preview}\\n\\n... (Total: {len(content):,} karakter)"')
                print(f"Fixed content return line {i+1}")
                i += 1
            continue
        else:
            new_lines.append(line)
        i += 1
    
    content = '\n'.join(new_lines)
    with open('kuera_web_server.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Done!")
else:
    print("Not found")
