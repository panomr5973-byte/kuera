#!/usr/bin/env python3
\"\"\"Auto-fix kuera_web_server.py indentation\"\"\"

import re
from pathlib import Path

file_path = Path('kuera_web_server.py')

with open(file_path) as f:
  lines = f.readlines()

# Fix search_knowledge indentation (line ~141)
fixed_lines = []
in_search_knowledge = False
indent_level = 0

for i, line in enumerate(lines):
  stripped = line.strip()
  
  if 'def search_knowledge(self, query, limit=1):' in stripped:
    in_search_knowledge = True
    indent_level = len(line) - len(line.lstrip())
    fixed_lines.append(line)
    continue
  
  if in_search_knowledge:
    if stripped.startswith('query_lower ='):
      # Fix indent
      new_line = ' ' * indent_level + '    ' + stripped + '\n'
      fixed_lines.append(new_line)
    elif 'db.close()' in stripped:
      in_search_knowledge = False
    else:
      # Keep other lines as is
      fixed_lines.append(line)
  else:
    fixed_lines.append(line)

with open(file_path, 'w') as f:
  f.writelines(fixed_lines)

print("Fixed indentation in kuera_web_server.py")
print("Run: python kuera_web_server.py")

