# Backend Setup Guide for Teammates

## Quick Start (For New Developers)

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python setup_db.py
```

This will:

- Create the SQLite database file (`eduassess.db`)
- Create all necessary tables
- Prepare the system for use

### 3. Run the Backend

```bash
python main.py
```

The API will be available at: `http://localhost:8000`

## Common Issues

### "No such table" errors

**Solution:** Run `python setup_db.py` to create database tables

### "Database is locked" errors

**Solution:** Make sure only one instance of the backend is running

### "Module not found" errors

**Solution:** Install dependencies: `pip install -r requirements.txt`

## Database Location

- SQLite file: `backend/eduassess.db`
- This file is gitignored (not committed)
- Each developer has their own local database

## First Time Setup Checklist

- [ ] Python 3.10+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database initialized (`python setup_db.py`)
- [ ] Backend running (`python main.py`)
- [ ] Can access http://localhost:8000/docs

## Need Help?

Check the main README.md or ask in the team chat!
