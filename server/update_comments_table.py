import sqlite3

conn = sqlite3.connect("comments.db")
cursor = conn.cursor()

# Eğer 'likes' sütunu yoksa ekle
cursor.execute("ALTER TABLE comments ADD COLUMN likes INTEGER DEFAULT 0")

conn.commit()
conn.close()

print("✅ likes sütunu eklendi.")
