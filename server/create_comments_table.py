import sqlite3

# Veritabanı bağlantısı
conn = sqlite3.connect("comments.db")

# comments tablosu: her yorum hangi hisseye ve kullanıcıya ait, ne yazmış ve ne zaman
conn.execute("""
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    username TEXT NOT NULL,
    comment TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("✅ Yorum tablosu oluşturuldu.")
