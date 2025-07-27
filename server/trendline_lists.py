import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

# --- 1) Yol tanımları
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRICES_DB_PATH = os.path.join(BASE_DIR, "hissedata.db")
SIGNALS_DB_PATH = os.path.join(BASE_DIR, "trendline_signals.db")

# --- 2) Tabloyu oluştur
def create_trendline_table():
    conn = sqlite3.connect(SIGNALS_DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trendline_signals (
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

# --- 3) Sadece son trendline sinyalini bul ve kaydet
def get_latest_trendline_signals():
    create_trendline_table()

    # Fiyat verisini oku
    conn_prices = sqlite3.connect(PRICES_DB_PATH)
    df_all = pd.read_sql_query("SELECT * FROM prices", conn_prices)
    conn_prices.close()

    df_all["date"] = pd.to_datetime(df_all["date"])
    df_all.sort_values(["symbol", "date"], inplace=True)

    lookback = 30
    maxlen = 700

    results = []
    conn = sqlite3.connect(SIGNALS_DB_PATH)
    cursor = conn.cursor()

    for symbol, df in df_all.groupby("symbol"):
        if len(df) < lookback + 1:
            continue

        df = df.tail(maxlen).copy()
        df.set_index("date", inplace=True)

        if not {"open", "high", "low", "close"}.issubset(df.columns):
            continue

        def check_trend_line(support, pivot, slope, y):
            intercept = -slope * pivot + y[pivot]
            line_vals = slope * np.arange(len(y)) + intercept
            diffs = line_vals - y
            if support and diffs.max() > 1e-5: return -1.0
            if not support and diffs.min() < -1e-5: return -1.0
            return (diffs**2).sum()

        def optimize_slope(support, pivot, init_slope, y):
            slope_unit = (y.max() - y.min()) / len(y)
            opt_step, min_step = 1.0, 0.0001
            best_slope, best_err = init_slope, check_trend_line(support, pivot, init_slope, y)
            curr_step, get_derivative = opt_step, True
            while curr_step > min_step:
                if get_derivative:
                    delta = slope_unit * min_step
                    test_err = check_trend_line(support, pivot, best_slope + delta, y)
                    derivative = test_err - best_err
                    if test_err < 0:
                        test_err = check_trend_line(support, pivot, best_slope - delta, y)
                        derivative = best_err - test_err
                    if test_err < 0: break
                    get_derivative = False
                delta_slope = slope_unit * curr_step
                test_slope = best_slope - delta_slope if derivative > 0 else best_slope + delta_slope
                test_err = check_trend_line(support, pivot, test_slope, y)
                if test_err < 0 or test_err >= best_err:
                    curr_step *= 0.5
                else:
                    best_slope, best_err = test_slope, test_err
                    get_derivative = True
            intercept = -best_slope * pivot + y[pivot]
            return best_slope, intercept

        def fit_trendlines(high, low, close):
            x = np.arange(len(close))
            coefs = np.polyfit(x, close, 1)
            fitted = coefs[0] * x + coefs[1]
            upper_pivot = (high - fitted).argmax()
            lower_pivot = (low - fitted).argmin()
            support = optimize_slope(True, lower_pivot, coefs[0], low)
            resist = optimize_slope(False, upper_pivot, coefs[0], high)
            return support, resist

        # SADECE SON SİNYAL ARANIYOR
        last_signal = None
        i = 0
        while i + lookback < len(df):
            w = df.iloc[i:i + lookback]
            sup_coef, res_coef = fit_trendlines(w["high"].values, w["low"].values, w["close"].values)

            if i + lookback >= len(df):
                break

            next_close = df.iloc[i + lookback]["close"]
            next_date = df.index[i + lookback]
            sup_val = sup_coef[0] * lookback + sup_coef[1]
            res_val = res_coef[0] * lookback + res_coef[1]

            if next_close < sup_val * 0.995:
                last_signal = ("SELL", next_date, next_close)
                break
            elif next_close > res_val * 1.005:
                last_signal = ("BUY", next_date, next_close)
                break

            i += 1

        if last_signal:
            signal_type, signal_date, signal_price = last_signal
            current_price = round(df["close"].iloc[-1], 2)
            change_percent = round(100 * (current_price - signal_price) / signal_price, 2)
            record = {
                "symbol": symbol,
                "signal": signal_type,
                "date": signal_date.strftime('%Y-%m-%d'),
                "signal_price": round(signal_price, 2),
                "current_price": current_price,
                "change_percent": change_percent
            }
            results.append(record)

            cursor.execute('''
                INSERT OR IGNORE INTO trendline_signals
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
    sigs = get_latest_trendline_signals()
    print(f"Trendline: {len(sigs)} hisse için son sinyal kaydedildi.")
