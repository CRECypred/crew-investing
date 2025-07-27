import pandas as pd
import yfinance as yf
import sqlite3
from datetime import datetime, timedelta

DB_PATH  = "C:/Users/alper/Desktop/crew-investing/server/hissedata.db"
CSV_PATH = "C:/Users/alper/Desktop/crew-investing/server/bist.csv"

# Sembol listesini oku
df_symbols = pd.read_csv(CSV_PATH)
symbols = df_symbols['symbol'].dropna().unique().tolist()

# Veritabanına bağlan ve cursor oluştur
conn   = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1) Tabloyu oluştur (varsa pas geç)
cursor.execute("""
CREATE TABLE IF NOT EXISTS prices (
    date   TEXT,
    open   REAL,
    high   REAL,
    low    REAL,
    close  REAL,
    symbol TEXT
);
""")
conn.commit()

for symbol in symbols:
    # 2) O sembolün en son tarihini oku
    result = pd.read_sql_query(
        "SELECT MAX(date) AS last_date FROM prices WHERE symbol = ?",
        conn,
        params=(symbol,)
    )
    last_date = result.at[0, "last_date"]  # None ya da 'YYYY-MM-DD'

    # 3) YFinance parametrelerini ayarla
    if last_date is None:
        # Hiç veri yoksa 400 günlük geçmişi çek
        start  = None
        period = "400d"
    else:
        # Bir sonraki günden başla
        dt      = datetime.strptime(last_date, "%Y-%m-%d") + timedelta(days=1)
        start   = dt.strftime("%Y-%m-%d")
        period  = None

    try:
        print(f"İndiriliyor: {symbol} (start={start or period})")
        df = yf.download(
            symbol,
            start=start,
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False
        )

        if df.empty:
            print(f"{symbol} → ❌ veri güncellemesi yok.")
            continue

        # Kolonları düzenle
        df = df.reset_index()[['Date','Open','High','Low','Close']]
        df.columns = ['date','open','high','low','close']
        df['symbol'] = symbol

        # Yeni verileri ekle
        df.to_sql("prices", conn, if_exists="append", index=False)
        print(f"{symbol} → ✅ {len(df)} yeni gün eklendi.")

    except Exception as e:
        print(f"{symbol} → ⚠️ Hata: {e}")

# Bağlantıyı kapat
conn.close()
