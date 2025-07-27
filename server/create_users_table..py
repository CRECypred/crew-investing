import sqlite3

# Veritabanı bağlantısını oluştur
conn = sqlite3.connect("users.db")

# users tablosunu oluştur (yoksa)
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# role sütununu ekle (varsa hata vermez)
try:
    conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    print("✅ 'role' sütunu eklendi.")
except sqlite3.OperationalError:
    print("ℹ️ 'role' sütunu zaten mevcut, atlandı.")

# Kaydet ve kapat
conn.commit()
conn.close()

print("Kullanıcı tablosu kontrol edildi.")
