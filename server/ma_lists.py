import os
import sqlite3
import pandas as pd

# --- 1) Yol tanımları
BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
PRICES_DB_PATH   = os.path.join(BASE_DIR, "hissedata.db")
SIGNALS_DB_PATH  = os.path.join(BASE_DIR, "signals.db")

# --- 2) signals.db ve tabloyu oluşturma
def create_signals_table():
    with sqlite3.connect(SIGNALS_DB_PATH, timeout=10) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS ma_signals (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol         TEXT    NOT NULL,
                signal         TEXT    NOT NULL,
                date           TEXT    NOT NULL,
                signal_price   REAL    NOT NULL,
                current_price  REAL    NOT NULL,
                change_percent REAL    NOT NULL,
                short_window   INTEGER NOT NULL,
                long_window    INTEGER NOT NULL,
                UNIQUE(symbol, short_window, long_window, date)
            );
        ''')
        conn.commit()

# --- 3) Sinyalleri hesaplayıp signals.db'ye yaz
def get_latest_signals(short_window, long_window):
    create_signals_table()

    # Fiyat verisini oku
    with sqlite3.connect(PRICES_DB_PATH, timeout=10) as conn_prices:
        df_all = pd.read_sql_query("SELECT * FROM prices", conn_prices)

    df_all['date'] = pd.to_datetime(df_all['date'])
    df_all.sort_values(['symbol', 'date'], inplace=True)

    results = []

    with sqlite3.connect(SIGNALS_DB_PATH, timeout=10) as conn_sig:
        c_sig = conn_sig.cursor()

        for symbol, df_symbol in df_all.groupby("symbol"):
            df = df_symbol.copy()
            df[f"ma{short_window}"] = df["close"].rolling(window=short_window).mean()
            df[f"ma{long_window}"] = df["close"].rolling(window=long_window).mean()
            df.dropna(inplace=True)

            prev_diff = df[f"ma{short_window}"].shift(1) - df[f"ma{long_window}"].shift(1)
            curr_diff = df[f"ma{short_window}"] - df[f"ma{long_window}"]
            crossover = prev_diff * curr_diff < 0

            df_signal = df[crossover]
            if not df_signal.empty:
                last_row      = df_signal.iloc[-1]
                signal        = "AL" if last_row[f"ma{short_window}"] > last_row[f"ma{long_window}"] else "SAT"
                signal_price  = last_row["close"]
                current_price = df.iloc[-1]["close"]
                change_percent = 100 * (current_price - signal_price) / signal_price

                rec = {
                    "symbol":         symbol,
                    "signal":         signal,
                    "date":           last_row["date"].strftime("%Y-%m-%d"),
                    "signal_price":   round(signal_price, 2),
                    "current_price":  round(current_price, 2),
                    "change_percent": round(change_percent, 2),
                    "short_window":   short_window,
                    "long_window":    long_window
                }
                results.append(rec)

                c_sig.execute('''
                    INSERT OR IGNORE INTO ma_signals
                      (symbol, signal, date, signal_price, current_price, change_percent, short_window, long_window)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    rec["symbol"],
                    rec["signal"],
                    rec["date"],
                    rec["signal_price"],
                    rec["current_price"],
                    rec["change_percent"],
                    rec["short_window"],
                    rec["long_window"]
                ))

        conn_sig.commit()

    return results

# --- 4) Test
if __name__ == "__main__":
    windows = [(8, 22), (22, 50), (50, 200)]
    for sw, lw in windows:
        sigs = get_latest_signals(sw, lw)
        print(f"{sw}/{lw} → {len(sigs)} yeni sinyal kaydedildi.")
