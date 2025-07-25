import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("UPDATE users SET avatar_url = ? WHERE username = ?", ("/static/avatars/Cypred.png", "Cypred"))
conn.commit()
conn.close()

print("✅ Avatar URL güncellendi.")
