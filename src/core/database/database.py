import sqlite3
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'test.db')
DATABASE_USER = os.getenv('DATABASE_USER', 'test')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'test')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'test')

def get_connection():
    conn = sqlite3.connect(DATABASE_URL)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            owner_id INTEGER,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()