# KUERA AI — Push ke GitHub (Backup)

**Email:** panomr5973@gmail.com  
**Git Config:** Sudah di-update ke email di atas

---

## Cara Manual (Paling Aman)

### Step 1: Buat Repository di GitHub
1. Buka browser: https://github.com/new
2. Isi **Repository name**: `AI-Project` (atau nama lain)
3. **Jangan centang** "Add a README file" (sudah ada di project)
4. Klik **"Create repository"**

### Step 2: Copy URL
Setelah repo dibuat, copy URL-nya. Contoh:
```
https://github.com/panomr5973/AI-Project.git
```

### Step 3: Push dari CMD/PowerShell
Buka PowerShell di folder project ini, lalu jalankan:

```bash
cd D:\workspace\ai_core\AI-Project

# Tambahkan remote
git remote add origin https://github.com/panomr5973/AI-Project.git

# Push semua commit
git push -u origin master
```

### Step 4: Login GitHub
Saat diminta password, gunakan **Personal Access Token**, bukan password GitHub biasa.

**Cara buat token:**
1. Buka: https://github.com/settings/tokens
2. Klik **"Generate new token (classic)"**
3. Centang **"repo"** (full control)
4. Klik **"Generate token"**
5. Copy token dan paste sebagai password

---

## Cara Otomatis (Script)

Double-click atau jalankan di PowerShell:
```powershell
.\push_to_github.ps1
```

Script akan:
1. Cek git config
2. Tanya URL repo GitHub
3. Push otomatis

---

## Apa yang Sudah di-Commit?

```
b45ddd4 docs: infrastructure audit
f0a8c5a feat: Phase 3 integration — Audit Toolkit + WorldBank connectors
0cc19c4 chore: add run.bat
fcc75e1 refactor: modularize unified desktop into src/ architecture
a74b125 feat: retroactive memory, memory agent, LLM context injection
550ecd6 chore: initialize repo
```

**Total:** 6 commit dengan ~1,500+ baris perubahan.

---

## Note Penting

- **File besar tidak di-commit**: `.gguf` models, `venv/`, `ai_env/` di-exclude via `.gitignore`
- **Database tidak di-commit**: `data/*.db` di-exclude (terlalu besar)
- **Memory dan diary di-commit**: `memory/`, `memorized_diary/`, `MEMORY.md` sudah masuk

Kalau butuh bantuan step-by-step, bilang saja.
