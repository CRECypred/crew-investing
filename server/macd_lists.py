import os
import sqlite3
import pandas as pd

# --- 1) Yol tanımları
BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
PRICES_DB_PATH   = os.path.join(BASE_DIR, "hissedata.db")
SIGNALS_DB_PATH  = os.path.join(BASE_DIR, "macd_signals.db")

# --- 2) signals.db ve tabloyu oluşturma
def create_macd_table():
    conn = sqlite3.connect(SIGNALS_DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS macd_signals (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol         TEXT    NOT NULL,
            signal         TEXT    NOT NULL,    -- 'AL' veya 'SAT'
            date           TEXT    NOT NULL,    -- YYYY‑MM‑DD
            signal_price   REAL    NOT NULL,
            current_price  REAL    NOT NULL,
            change_percent REAL    NOT NULL,
            UNIQUE(symbol, date)
        );
    ''')
    conn.commit()
    conn.close()

# --- 3) MACD sinyallerini hesapla ve kaydet
def get_latest_macd_signals():
    create_macd_table()

    # 3.1) Fiyat verilerini oku
    conn_prices = sqlite3.connect(PRICES_DB_PATH)
    df_all = pd.read_sql_query("SELECT * FROM prices", conn_prices)
    conn_prices.close()

    df_all['date'] = pd.to_datetime(df_all['date'])
    df_all.sort_values(['symbol', 'date'], inplace=True)

    results = []
    conn_sig = sqlite3.connect(SIGNALS_DB_PATH)
    c_sig = conn_sig.cursor()

    for symbol, df in df_all.groupby("symbol"):
        df = df.copy()

        # EMA'lar
        df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
        df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()

        # MACD ve Sinyal
        df["macd"] = df["ema12"] - df["ema26"]
        df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        df.dropna(inplace=True)

        prev_diff = (df["macd"] - df["signal"]).shift(1)
        curr_diff = (df["macd"] - df["signal"])
        crossover = prev_diff * curr_diff < 0

        df_signal = df[crossover]
        if not df_signal.empty:
            last_row = df_signal.iloc[-1]
            signal_type = "AL" if last_row["macd"] > last_row["signal"] else "SAT"
            signal_price = last_row["close"]
            current_price = df.iloc[-1]["close"]
            change_percent = 100 * (current_price - signal_price) / signal_price

            rec = {
                "symbol": symbol,
                "signal": signal_type,
                "date": last_row["date"].strftime("%Y-%m-%d"),
                "signal_price": round(signal_price, 2),
                "current_price": round(current_price, 2),
                "change_percent": round(change_percent, 2)
            }
            results.append(rec)

            c_sig.execute('''
                INSERT OR IGNORE INTO macd_signals
                  (symbol, signal, date, signal_price, current_price, change_percent)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                rec["symbol"],
                rec["signal"],
                rec["date"],
                rec["signal_price"],
                rec["current_price"],
                rec["change_percent"]
            ))

    conn_sig.commit()
    conn_sig.close()

    return results

# --- 4) Örnek kullanım
if __name__ == "__main__":
    sigs = get_latest_macd_signals()
    print(f"MACD: {len(sigs)} yeni sinyal kaydedildi.")
