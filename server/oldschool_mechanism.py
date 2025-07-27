import sqlite3
import pandas as pd

# 1) Ayarlar
START_DATE = "2025-07-01"
MA_DB = "C:/Users/alper/Desktop/crew-investing/server/signals.db"
MACD_DB = "C:/Users/alper/Desktop/crew-investing/server/macd_signals.db"
PRICES_DB = "C:/Users/alper/Desktop/crew-investing/server/hissedata.db"
RESULTS_DB = "C:/Users/alper/Desktop/crew-investing/server/oldschool_results.db"

# 2) Fiyat verisi
conn_prices = sqlite3.connect(PRICES_DB)
df_prices = pd.read_sql_query("SELECT date, symbol, close FROM prices", conn_prices, parse_dates=["date"])
conn_prices.close()
df_prices.sort_values(["symbol", "date"], inplace=True)
df_prices["prev_close"] = df_prices.groupby("symbol")["close"].shift(1)
df_prices["daily_return"] = (df_prices["close"] - df_prices["prev_close"]) / df_prices["prev_close"]
df_prices = df_prices[df_prices["date"] >= START_DATE]

# 3) MA(8/22) sinyalleri
conn_ma = sqlite3.connect(MA_DB)
df_ma = pd.read_sql_query(
    "SELECT symbol, date, signal FROM ma_signals WHERE short_window=8 AND long_window=22",
    conn_ma,
    parse_dates=["date"]
)
conn_ma.close()

# 4) MACD sinyalleri
conn_macd = sqlite3.connect(MACD_DB)
df_macd = pd.read_sql_query(
    "SELECT symbol, date, signal FROM macd_signals",
    conn_macd,
    parse_dates=["date"]
)
conn_macd.close()

# 5) Sinyal eşleşmelerini bul (5 gün içinde gelen eşler)
def find_matched_signals(ma_df, macd_df, signal_type):
    matched = []
    for symbol in ma_df["symbol"].unique():
        ma_dates = ma_df[(ma_df["symbol"] == symbol) & (ma_df["signal"] == signal_type)]["date"]
        macd_dates = macd_df[(macd_df["symbol"] == symbol) & (macd_df["signal"] == signal_type)]["date"]

        for ma_date in ma_dates:
            if any((macd_dates - ma_date).dt.days.between(0, 5)):
                matched.append(symbol)
                break  # Eşleşme varsa ekle ve çık

        for macd_date in macd_dates:
            if any((ma_dates - macd_date).dt.days.between(0, 5)):
                matched.append(symbol)
                break

    return list(set(matched))

buy_symbols = find_matched_signals(df_ma, df_macd, "BUY")
sell_symbols = find_matched_signals(df_ma, df_macd, "SELL")

# 6) Veritabanı oluştur
conn_out = sqlite3.connect(RESULTS_DB)
cur = conn_out.cursor()
cur.execute("DROP TABLE IF EXISTS list_returns;")
cur.execute("""
    CREATE TABLE list_returns (
        date TEXT,
        list_name TEXT,
        daily_return REAL
    );
""")
conn_out.commit()

# 7) Günlük getiri hesapla
def write_returns_to_db(symbols, list_name):
    df_sub = df_prices[df_prices["symbol"].isin(symbols)]
    if df_sub.empty:
        return
    df_ret = (
        df_sub.groupby("date")["daily_return"]
        .mean()
        .reset_index()
        .assign(list_name=list_name)
    )
    df_ret.to_sql("list_returns", conn_out, if_exists="append", index=False)

write_returns_to_db(buy_symbols, "oldschool_buy")
write_returns_to_db(sell_symbols, "oldschool_sell")

conn_out.close()
print("✅ Oldschool listeleri için günlük getiriler hesaplandı ve oldschool_results.db’ye kaydedildi.")
