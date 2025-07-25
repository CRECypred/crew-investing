import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from most import MOSTScreener  # MOSTScreener sınıfını import et

# --- 1) Yol tanımları
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRICES_DB_PATH = os.path.join(BASE_DIR, "hissedata.db")
SIGNALS_DB_PATH = os.path.join(BASE_DIR, "most_signals.db")

# --- 2) Tabloyu oluştur
def create_most_table():
    conn = sqlite3.connect(SIGNALS_DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS most_signals (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol         TEXT    NOT NULL,
            signal         TEXT    NOT NULL,    -- 'BUY' veya 'SELL'
            date           TEXT    NOT NULL,    -- YYYY-MM-DD
            signal_price   REAL    NOT NULL,
            current_price  REAL    NOT NULL,
            change_percent REAL    NOT NULL,
            UNIQUE(symbol, date)
        );
    ''')
    conn.commit()
    conn.close()

# --- 3) MOST sinyallerini tespit et ve kaydet
def get_latest_most_signals():
    create_most_table()

    # Fiyat verisini oku
    conn_prices = sqlite3.connect(PRICES_DB_PATH)
    df_all = pd.read_sql_query("SELECT * FROM prices", conn_prices)
    conn_prices.close()

    df_all["date"] = pd.to_datetime(df_all["date"])
    df_all.sort_values(["symbol", "date"], inplace=True)

    results = []
    conn = sqlite3.connect(SIGNALS_DB_PATH)
    cursor = conn.cursor()

    for symbol, df in df_all.groupby("symbol"):
        df = df.copy()
        if len(df) < 60:
            continue

        df.set_index("date", inplace=True)
        if "close" not in df.columns:
            continue

        close = df["close"]

        try:
            screener = MOSTScreener(length=3, stop_loss_percent=2.0, ma_type="VAR")
            most_line, direction, signals, ma = screener.calculate_most(close)
        except Exception as e:
            print(f"{symbol} hata: {e}")
            continue

        # Son geçerli sinyali bul
        last_valid_signal = signals[signals.abs() == 2]
        if last_valid_signal.empty:
            continue

        last_date = last_valid_signal.index[-1]
        signal_type = "BUY" if last_valid_signal.iloc[-1] == 2 else "SELL"
        signal_price = close.loc[last_date]
        current_price = close.iloc[-1]
        change_percent = round(100 * (current_price - signal_price) / signal_price, 2)

        record = {
            "symbol": symbol,
            "signal": signal_type,
            "date": last_date.strftime("%Y-%m-%d"),
            "signal_price": round(signal_price, 2),
            "current_price": round(current_price, 2),
            "change_percent": change_percent
        }
        results.append(record)

        cursor.execute('''
            INSERT OR IGNORE INTO most_signals
            (symbol, signal, date, signal_price, current_price, change_percent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            record["symbol"],
            record["signal"],
            record["date"],
            record["signal_price"],
            record["current_price"],
            record["change_percent"]
        ))

    conn.commit()
    conn.close()
    return results

# --- 4) Örnek kullanım
if __name__ == "__main__":
    sigs = get_latest_most_signals()
    print(f"MOST: {len(sigs)} hisse için son sinyal kaydedildi.")
