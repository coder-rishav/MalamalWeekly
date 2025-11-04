# Running the Django Development Server

## Problem
When running `python manage.py runserver`, you might get errors like:
- "Razorpay library not installed"
- "Module not found" errors

This happens because `python` might be using your system Python instead of the virtual environment Python where packages are installed.

## Solutions

### Option 1: Use the Convenience Scripts (Easiest)

#### For PowerShell:
```powershell
.\run_server.ps1
```

#### For Command Prompt / Double-click:
```cmd
run_server.bat
```
Just double-click `run_server.bat` in File Explorer!

### Option 2: Activate Virtual Environment First

#### For PowerShell:
```powershell
# Step 1: Activate virtual environment
.\venv\Scripts\Activate.ps1

# Step 2: Run server (now 'python' points to venv Python)
python manage.py runserver
```

#### For Command Prompt:
```cmd
# Step 1: Activate virtual environment
venv\Scripts\activate.bat

# Step 2: Run server
python manage.py runserver
```

### Option 3: Use Full Path (No Activation Needed)

#### For PowerShell:
```powershell
.\venv\Scripts\python.exe manage.py runserver
```

#### For Command Prompt:
```cmd
venv\Scripts\python.exe manage.py runserver
```

## Why This Happens

Your system might have multiple Python installations:
- **System Python**: C:\Python312\python.exe (or similar)
- **Virtual Environment Python**: C:\...\MalamalWeekly\venv\Scripts\python.exe

When you run `python manage.py runserver`:
- ❌ Without activation: Uses system Python (no packages installed)
- ✅ With activation or full path: Uses venv Python (all packages installed)

## Checking Which Python You're Using

```powershell
# Check which Python will be used
python --version
where.exe python

# After activating venv, you should see (venv) in your prompt:
# (venv) PS C:\...\MalamalWeekly>
```

## Installing Packages

Always make sure virtual environment is activated before installing packages:

```powershell
# Activate venv first
.\venv\Scripts\Activate.ps1

# Then install packages
pip install razorpay stripe django

# Or install from requirements.txt
pip install -r requirements.txt
```

## Quick Reference

| Method | Command | Pros | Cons |
|--------|---------|------|------|
| Script (PS) | `.\run_server.ps1` | Easiest, auto-stops old servers | PowerShell only |
| Script (Batch) | `run_server.bat` or double-click | Very easy, works everywhere | Windows only |
| Activate + Run | `.\venv\Scripts\Activate.ps1` then `python manage.py runserver` | Standard Django way | Two steps |
| Full Path | `.\venv\Scripts\python.exe manage.py runserver` | No activation needed | Long command |

## Recommended Workflow

1. **Development**: Use `.\run_server.ps1` or double-click `run_server.bat`
2. **Production**: Never use `runserver`, use proper WSGI server (gunicorn, uwsgi)

---

**Pro Tip**: Add `run_server.bat` to your taskbar for one-click server startup! 🚀
