import sqlite3
import os

DATABASE_URL = os.getenv('DB_HOST', 'test.db')
DATABASE_PORT = os.getenv('DB_PORT', '3306')
DATABASE_USER = os.getenv('DB_USER', 'test')
DATABASE_PASSWORD = os.getenv('DB_PASSWORD', 'test')
DATABASE_NAME = os.getenv('DB_NAME', 'test')

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