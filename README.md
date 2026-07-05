# Side Quest App

A social gamification platform where friends create challenges for each other, submit photo proof, and compete on leaderboards.

**Live:** https://side-quest-app.onrender.com

---

## Features

| Feature | Description |
|---|---|
| User accounts | Auto-create accounts on first login with hashed passwords |
| Friends | Add friends, bidirectional relationships |
| Side quests | Personal todo-style quests for +5 points each |
| Direct challenges | 1-on-1 challenges with easy/medium/hard tiers (10/25/50 pts) |
| Groups | Create groups, add members, group-scoped challenges |
| Group challenges | Random challenger pick, 24h deadlines, proof submission + review |
| Leaderboards | Per-group rankings with medal badges for top 3 |

## Tech Stack

- **Backend:** Python 3 / Flask 3 / SQLAlchemy / Gunicorn
- **Database:** PostgreSQL (Supabase) with SQLite fallback
- **Frontend:** Vanilla HTML / CSS / JavaScript (zero dependencies)

## Project Structure

```
├── backend/
│   ├── app.py              # Flask API + SQLAlchemy models
│   ├── requirements.txt    # Python dependencies
│   ├── init_db.py          # Standalone DB init script
│   └── data.json           # Seed data (7 test users, 2 groups)
├── frontend/
│   ├── index.html          # Single-page app
│   ├── script.js           # Client-side logic
│   └── style.css           # Styling
├── Procfile                # Render/Herkou start command
├── render.yaml             # Render Blueprint config
├── runtime.txt             # Python version pin
└── DEPLOYMENT.md           # Deployment guide
```

## API Endpoints

| Method | Route | Description |
|---|---|---|
| POST | `/api/login` | Login or auto-create user |
| POST | `/api/friend/add` | Add a friend |
| GET | `/api/friends/<username>` | List friends |
| GET | `/api/sidequests/<username>` | Get side quests |
| POST | `/api/sidequest/add` | Create side quest |
| POST | `/api/sidequest/<id>/complete` | Complete quest (+5 pts) |
| POST | `/api/sidequest/<id>/delete` | Delete quest |
| POST | `/api/challenge/create` | Create 1-on-1 challenge |
| POST | `/api/challenge/upload-proof` | Upload proof (base64) |
| POST | `/api/challenge/review` | Accept/reject proof |
| GET | `/api/challenges/sent/<username>` | Challenges sent |
| GET | `/api/challenges/received/<username>` | Challenges received |
| GET | `/api/user/<username>/points` | Get user points |
| POST | `/api/group/create` | Create group |
| POST | `/api/group/<id>/add-member` | Add member |
| POST | `/api/group/<id>/pick-challenger` | Random challenger pick |
| POST | `/api/group-challenge/<id>/define` | Define challenge |
| POST | `/api/group-challenge/<id>/submit` | Submit proof |
| POST | `/api/group-challenge/<id>/review` | Review submission |
| GET | `/api/group/<id>/leaderboard` | Group leaderboard |
| GET | `/api/groups/user/<username>` | User's groups |
| `/*` | All other routes | Serve frontend static files |

## Running Locally

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000` in a browser.

## Deploying

The app auto-deploys on push to `main` via Render. Configuration lives in `render.yaml`.

**Required env var:** `DATABASE_URL` — a PostgreSQL connection string. Defaults to SQLite if absent.

---

## Changelog

### 2026-07-05 — Security & Feature Update

- **Security:** Passwords hashed with werkzeug's scrypt (no more plain-text in DB)
- **Security:** All API inputs sanitized (length limits, username whitelist `[a-zA-Z0-9_-]`)
- **Security:** All user-generated frontend content HTML-escaped (XSS prevention)
- **Security:** Legacy plain-text passwords auto-upgraded to hashes on startup
- **Feature:** Side quests UI added (create, complete, delete from dashboard)
- **Feature:** Total points counter added to header
- **Fix:** Removed dead code (`loadLeaderboard`, deprecated `createGroupChallenge`)
- **Fix:** `db.create_all()` moved outside `__main__` for gunicorn compatibility
- **Infra:** Switched from Flask dev server to gunicorn (production WSGI)
- **Infra:** Added `Procfile`, `render.yaml`, `runtime.txt`
- **Infra:** Connected to Supabase PostgreSQL on Render for persistent data
