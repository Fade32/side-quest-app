#!/usr/bin/env python
"""
Database initialization script
Run this once to create all tables in PostgreSQL
"""
from app import app, db, migrate_json_to_db

if __name__ == '__main__':
    with app.app_context():
        print('Creating database tables...')
        db.create_all()
        print('Migrating existing JSON data (if present)...')
        migrate_json_to_db()
        print('✅ Database tables created successfully!')
