#!/usr/bin/env python
with open('kuera_persona.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find line 273-284 and replace
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Find the _general_response method
    if 'def _general_response' in line:
        # Replace the entire method
        new_lines.append('    def _general_response(self, message: str) -> str:\n')
        new_lines.append('        """General response - more personal and natural"""\n')
        new_lines.append('        # This would normally call the actual AI model\n')
        new_lines.append("        short_msg = message[:50] + ('...' if len(message) > 50 else '')\n")
        new_lines.append('        return f"Saya mengerti tentang \'{short_msg}\'. Saya akan bantu sebisanya."\n')
        
        # Skip until we find the next method (def _get_day_number)
        i += 1
        while i < len(lines) and 'def _get_day_number' not in lines[i]:
            i += 1
        # Now i points to _get_day_number line, which will be added in next iteration
        continue
    else:
        new_lines.append(line)
    
    i += 1

with open('kuera_persona.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("[OK] Updated _general_response method")
