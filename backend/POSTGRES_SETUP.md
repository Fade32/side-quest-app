# PostgreSQL Setup Guide

## 1. Install PostgreSQL

### macOS (Homebrew)
```bash
brew install postgresql
brew services start postgresql
```

### Windows
Download from: https://www.postgresql.org/download/windows/

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

## 2. Create Database

```bash
psql -U postgres
CREATE DATABASE side_quest;
\q
```

## 3. Set Environment Variables

Copy `.env.example` to `.env` and update:
```bash
cp .env.example .env
```

Edit `.env`:
```
DATABASE_URL=postgresql://username:password@localhost:5432/side_quest
```

## 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 5. Initialize Database

```bash
python init_db.py
```

## 6. Run the App

```bash
python app.py
```

## Free PostgreSQL Hosting Options

- **Render**: https://render.com (free tier available)
- **Railway**: https://railway.app (free credits)
- **Heroku Postgres**: https://www.heroku.com/postgres (paid, but popular)
- **Supabase**: https://supabase.com (free tier with 500MB)
- **neon**: https://neon.tech (free tier with 3GB)

## Example: Deploy to Render

1. Create `.env` with Render's database URL
2. Push to GitHub
3. Connect to Render's GitHub integration
4. Render automatically deploys and sets environment variables
