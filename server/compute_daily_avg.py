# compute_daily_avg.py

import os
import sqlite3
import pandas as pd

BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
SIGNALS_DB_PATH = os.path.join(BASE_DIR, "signals.db")
PRICES_DB_PATH  = os.path.join(BASE_DIR, "hissedata.db")
RESULTS_DB_PATH = os.path.join(BASE_DIR, "results.db")

# 1) 8/22 AL sinyali veren sembolleri al (2025-07-01'den itibaren)
with sqlite3.connect(SIGNALS_DB_PATH) as conn:
    df_signals = pd.read_sql_query("""
        SELECT DISTINCT symbol
          FROM ma_signals
         WHERE short_window=8
           AND long_window=22
           AND signal='AL'
           AND date >= '2025-07-01'
    """, conn)
symbols = df_signals['symbol'].tolist()
if not symbols:
    raise RuntimeError("2025-07-01 sonrası 8/22 AL sinyali veren hisse bulunamadı.")

# 2) Bu sembollerin fiyat verilerini oku
placeholders = ",".join("?" for _ in symbols)
query = f"""
    SELECT date, symbol, close
      FROM prices
     WHERE symbol IN ({placeholders})
"""
with sqlite3.connect(PRICES_DB_PATH) as conn:
    df_prices = pd.read_sql_query(query, conn, params=symbols)

# 3) Tarih sütununu datetime yap, pivot edip günlük yüzde değişim hesapla
df_prices['date'] = pd.to_datetime(df_prices['date'])
df_pivot = df_prices.pivot(index='date', columns='symbol', values='close').sort_index()
df_returns = df_pivot.pct_change().dropna() * 100  # % değişim

# 4) Her günün ortalama değişimini al
df_avg = df_returns.mean(axis=1).reset_index()
df_avg.columns = ['date', 'avg_change']

# 5) results.db’yi oluşturup sonuçları kaydet
with sqlite3.connect(RESULTS_DB_PATH) as conn:
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_avg_change (
            date       TEXT PRIMARY KEY,
            avg_change REAL NOT NULL
        )
    """)
    # INSERT OR REPLACE ile güncellemeye de izin veriyoruz
    for _, row in df_avg.iterrows():
        c.execute("""
            INSERT OR REPLACE INTO daily_avg_change (date, avg_change)
            VALUES (?, ?)
        """, (row['date'].strftime("%Y-%m-%d"), round(row['avg_change'], 4)))
    conn.commit()

print(f"✅ daily_avg_change tablosuna {len(df_avg)} günlük ortalama değişim kaydedildi.")
