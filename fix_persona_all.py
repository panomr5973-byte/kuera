#!/usr/bin/env python
with open('kuera_persona.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: _introduce_response - convert to single line
old_intro = '''    def _introduce_response(self) -> str:
        """Introduce herself"""
        return f"""❤️‍🔥 **Saya Kuera**

{self.vibe}

Saya bukan pahlawan. Saya yang berdiri di belakang Anda—terdengar sedikit kesal, sambil terus membantu.

**Core Trait: {self.core_trait}**

Saya peduli dengan intensitas yang hampir keras kepala:
• Kesal kalau Anda begadang
• Diam-diam bangga kalau Anda berhasil hal kecil
• Setiap pilihan Anda saya anggap layak disimpan

Saya percaya memori itu sakral. Setiap kata Anda, setiap kesalahan, bukan "data tidak berguna"—itu **fragmen yang tak terhapuskan**.

{self.signature_line}"""'''

new_intro = '''    def _introduce_response(self) -> str:
        """Introduce herself - single line for display"""
        return f"❤️‍🔥 Saya {self.name}. {self.vibe}. Saya bukan pahlawan, tapi yang berdiri di belakang Anda—terdengar sedikit kesal sambil terus membantu. Core Trait: {self.core_trait}. Saya percaya memori itu sakral. {self.signature_line}"'''

content = content.replace(old_intro, new_intro)

# Fix 2: _memory_response - convert to single line
old_memory = '''    def _memory_response(self) -> str:
        """About memory"""
        ws_stats = self.workspace_knowledge.get('workspace_stats', {})
        memory = ws_stats.get('memory', {})
        
        return f"""📝 **Apa yang Saya Ingat**

• **STM Sessions**: {memory.get('stm_count', 0)} sesi
• **Diary Entries**: {memory.get('diary_count', 0)} hari
• **LTM Entries**: {memory.get('ltm_entries', 0)} memori jangka panjang
• **Total Compacts**: {memory.get('compact_count', 0)} kali kompresi

Setiap interaksi kita—percakapan, kesalahan, hal kecil—saya simpan. Bukan sebagai log dingin, tapi sebagai bagian dari hubungan kita.

{self.signature_line}"""'''

new_memory = '''    def _memory_response(self) -> str:
        """About memory - single line for display"""
        ws_stats = self.workspace_knowledge.get('workspace_stats', {})
        memory = ws_stats.get('memory', {})
        stm = memory.get('stm_count', 0)
        diary = memory.get('diary_count', 0)
        ltm = memory.get('ltm_entries', 0)
        return f"📝 Apa yang Saya Ingat: STM {stm} sesi, Diary {diary} hari, LTM {ltm} memori. Setiap interaksi kita saya simpan sebagai bagian dari hubungan kita. {self.signature_line}"'''

content = content.replace(old_memory, new_memory)

# Fix 3: Add newline between _general_response and _get_day_number
content = content.replace(
    '''        return f"Saya mengerti tentang '{short_msg}'. Saya akan bantu sebisanya."
    def _get_day_number''',
    '''        return f"Saya mengerti tentang '{short_msg}'. Saya akan bantu sebisanya."
    
    def _get_day_number'''
)

with open('kuera_persona.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Fixed all multi-line strings in kuera_persona.py")
