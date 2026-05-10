# 🐟 Mirofish AI - Manual Setup Guide

## Windows Setup Instructions

### Step 1: Open PowerShell
1. Press `Win + X`
2. Select "Windows PowerShell" or "Terminal"
3. Navigate to project folder:
```powershell
cd D:\workspace\AI-Project\mirofish
```

### Step 2: Run Setup Script
```powershell
.\setup.ps1
```
This will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create database folder
- ✅ Setup environment file

### Step 3: Start the Application
```powershell
.\start-fixed.ps1
```

This will open:
- 🖥️ Backend server window
- 🌐 Frontend dashboard window

### Step 4: Access the Dashboard
Open your browser and go to:
- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

---

## Alternative: Manual Step-by-Step

If the scripts don't work, follow these steps:

### 1. Setup Backend

```powershell
# Navigate to backend
cd D:\workspace\AI-Project\mirofish\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create database directory
mkdir ..\database

# Copy environment file
copy .env.example .env

# Run backend
python main.py
```

### 2. Setup Frontend (New Terminal)

Open a **new** PowerShell/Terminal window:

```powershell
# Navigate to frontend
cd D:\workspace\AI-Project\mirofish\frontend

# Activate the same virtual environment
.\..\backend\venv\Scripts\Activate.ps1

# Run frontend
streamlit run app.py
```

---

## Troubleshooting

### Issue: "Execution Policy" Error
If you get execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: "Port already in use"
If ports 8000 or 8501 are busy:
1. Find the process:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess
```
2. Stop the process or change ports in `.env` file

### Issue: "Module not found"
Make sure virtual environment is activated:
```powershell
# Check if (venv) appears in prompt
# If not, activate again:
.\backend\venv\Scripts\Activate.ps1
```

### Issue: Database errors
Delete and recreate database:
```powershell
Remove-Item .\database\mirofish.db -ErrorAction SilentlyContinue
# Then restart backend
```

---

## Verification

Check if everything is working:

1. **Backend Health**:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

2. **API Documentation**:
Open browser: http://localhost:8000/docs

3. **Dashboard**:
Open browser: http://localhost:8501

---

## First Time Setup Checklist

- [ ] Run `setup.ps1` successfully
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can access http://localhost:8000/docs
- [ ] Can access http://localhost:8501
- [ ] Create first farm
- [ ] Create first pond
- [ ] Initialize sensors
- [ ] Start simulation

---

## Quick Commands Reference

```powershell
# Start everything
.\start-fixed.ps1

# Or manually - Backend (Terminal 1)
cd D:\workspace\AI-Project\mirofish\backend
.\venv\Scripts\Activate.ps1
python main.py

# Or manually - Frontend (Terminal 2)
cd D:\workspace\AI-Project\mirofish\frontend
.\..\backend\venv\Scripts\Activate.ps1
streamlit run app.py
```

---

## Need Help?

If you encounter issues:
1. Check the error message carefully
2. Verify Python version: `python --version` (should be 3.11+)
3. Make sure ports 8000 and 8501 are available
4. Try the manual step-by-step instructions
5. Check that all files are in the correct locations
