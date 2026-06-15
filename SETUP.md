# Setup Guide for Team Members

## 1. Prerequisites
- Python 3.11 or higher installed
- Git installed
- Invite accepted on GitHub

## 2. Clone the repo
```bash
git clone https://github.com/majaliwamin/ehealth_malawi.git
cd ehealth_malawi
```

## 3. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

## 4. Create `.env` file
Create `backend\.env` with this content:

```env
DEBUG=True
DATABASE_URL=sqlite+aiosqlite:///./ehealth_malawi.db
SYNC_DATABASE_URL=sqlite:///./ehealth_malawi.db
SECRET_KEY=emw-secret-key-change-in-production-2026
CORS_ORIGINS=*
OFFLINE_MODE=True
ENABLE_AI_FEATURES=False
```

## 5. Get the database file
The database (`ehealth_malawi.db`) is not on GitHub. Ask the project lead to email it to you, then place it in the `backend\` folder.

## 6. Run the server
```bash
python run.py
```

## 7. Open the app
Go to `http://localhost:8000` in your browser.

## Making changes
- Edit code in your local copy
- `git add .` + `git commit -m "what you changed"` + `git push` to share
- Before pushing, run `git pull` to get latest changes from others
