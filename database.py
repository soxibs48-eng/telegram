import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "music_bot.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Foydalanuvchilar jadvali
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Telegramga yuklangan qo'shiqlar kesh jadvali (qayta yuklab olmaslik uchun)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cached_tracks (
        video_id TEXT PRIMARY KEY,
        file_id TEXT NOT NULL,
        title TEXT,
        performer TEXT,
        duration INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def register_user(user_id: int, username: str, first_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO users (user_id, username, first_name, last_seen)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
        username = excluded.username,
        first_name = excluded.first_name,
        last_seen = CURRENT_TIMESTAMP
    """, (user_id, username or "", first_name or "", datetime.now()))
    conn.commit()
    conn.close()

def get_cached_track(video_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_id, title, performer, duration FROM cached_tracks WHERE video_id = ?", (video_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def save_cached_track(video_id: str, file_id: str, title: str, performer: str, duration: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO cached_tracks (video_id, file_id, title, performer, duration)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(video_id) DO UPDATE SET
        file_id = excluded.file_id,
        title = excluded.title,
        performer = excluded.performer,
        duration = excluded.duration
    """, (video_id, file_id, title, performer, duration))
    conn.commit()
    conn.close()

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as user_count FROM users")
    users = cursor.fetchone()["user_count"]
    cursor.execute("SELECT COUNT(*) as track_count FROM cached_tracks")
    tracks = cursor.fetchone()["track_count"]
    conn.close()
    return {"users": users, "tracks": tracks}
