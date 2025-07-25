import sqlite3
import pandas as pd
import os

# --- Yollar
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SIGNALS_DB = os.path.join(BASE_DIR, "signals.db")              # MA sinyalleri
MACD_DB = os.path.join(BASE_DIR, "macd_signals.db")             # MACD sinyalleri
OLDSCHOOL_DB = os.path.join(BASE_DIR, "oldschool_signals.db")  # Yeni DB

# --- Tabloyu oluştur
def create_table():
    conn = sqlite3.connect(OLDSCHOOL_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS oldschool_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            signal TEXT NOT NULL,             -- BUY / SELL
            date TEXT NOT NULL,
            signal_price REAL NOT NULL,
            current_price REAL NOT NULL,
            change_percent REAL NOT NULL,
            UNIQUE(symbol, signal, date)
        );
    """)
    conn.commit()
    conn.close()

# --- Sinyalleri eşleştir ve kaydet
def generate_oldschool_signals():
    create_table()

    # MA ve MACD sinyallerini oku
    conn1 = sqlite3.connect(SIGNALS_DB)
    ma_df = pd.read_sql_query("""
        SELECT symbol, date, signal, signal_price, current_price, change_percent
        FROM ma_signals
        WHERE short_window = 8 AND long_window = 22
    """, conn1, parse_dates=["date"])
    conn1.close()

    conn2 = sqlite3.connect(MACD_DB)
    macd_df = pd.read_sql_query("""
        SELECT symbol, date, signal, signal_price, current_price, change_percent
        FROM macd_signals
    """, conn2, parse_dates=["date"])
    conn2.close()

    # Sinyal tarihlerini datetime olarak ayarla
    ma_df["date"] = pd.to_datetime(ma_df["date"])
    macd_df["date"] = pd.to_datetime(macd_df["date"])

    results = []
    conn_out = sqlite3.connect(OLDSCHOOL_DB)
    cursor = conn_out.cursor()

    for symbol in sorted(set(ma_df["symbol"]).intersection(macd_df["symbol"])):
        ma_signals = ma_df[ma_df["symbol"] == symbol].sort_values("date")
        macd_signals = macd_df[macd_df["symbol"] == symbol].sort_values("date")

        for _, ma_row in ma_signals.iterrows():
            ma_date = ma_row["date"]
            ma_sig = ma_row["signal"]

            # 5 gün içinde eşleşen MACD var mı?
            macd_matches = macd_signals[
                (macd_signals["signal"] == ma_sig) &
                (macd_signals["date"] >= ma_date) &
                (macd_signals["date"] <= ma_date + pd.Timedelta(days=5))
            ]

            if not macd_matches.empty:
                # Eşleşme varsa bu sinyali kaydet
                record = {
                    "symbol": symbol,
                    "signal": "BUY" if ma_sig == "AL" else "SELL",
                    "date": ma_date.strftime("%Y-%m-%d"),
                    "signal_price": round(ma_row["signal_price"], 2),
                    "current_price": round(ma_row["current_price"], 2),
                    "change_percent": round(ma_row["change_percent"], 2),
                }
                results.append(record)

                cursor.execute("""
                    INSERT OR IGNORE INTO oldschool_signals
                    (symbol, signal, date, signal_price, current_price, change_percent)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    record["symbol"],
                    record["signal"],
                    record["date"],
                    record["signal_price"],
                    record["current_price"],
                    record["change_percent"]
                ))

    conn_out.commit()
    conn_out.close()

    print(f"✅ Toplam {len(results)} oldschool sinyali kaydedildi.")


# --- Çalıştır
if __name__ == "__main__":
    generate_oldschool_signals()
