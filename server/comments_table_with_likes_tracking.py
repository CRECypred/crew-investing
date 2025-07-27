# update_comments_table_with_likes_tracking.py
import sqlite3

conn = sqlite3.connect("comments.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    UNIQUE(comment_id, username)  -- Bir kullanıcı aynı yoruma sadece 1 kez beğeni atabilir
)
""")

conn.commit()
conn.close()

print("✅ likes tablosu oluşturuldu.")
