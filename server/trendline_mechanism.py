import sqlite3
import pandas as pd

# 1) Ayarlar
START_DATE = "2025-07-01"
SIGNALS_DB = "C:/Users/alper/Desktop/crew-investing/server/trendline_signals.db"
PRICES_DB  = "C:/Users/alper/Desktop/crew-investing/server/hissedata.db"
RESULTS_DB = "C:/Users/alper/Desktop/crew-investing/server/trendline_results.db"

# 2) Hisse fiyatlarını oku
conn_prices = sqlite3.connect(PRICES_DB)
df_prices = pd.read_sql_query(
    "SELECT date, symbol, close FROM prices",
    conn_prices,
    parse_dates=["date"]
)
conn_prices.close()
df_prices.sort_values(["symbol", "date"], inplace=True)

# 3) Günlük getiriyi hesapla
df_prices["prev_close"] = df_prices.groupby("symbol")["close"].shift(1)
df_prices["daily_return"] = (
    df_prices["close"] - df_prices["prev_close"]
) / df_prices["prev_close"]
df_prices = df_prices[df_prices["date"] >= START_DATE]

# 4) Trendline sinyallerini oku (✅ tablo adı düzeltildi)
conn_sig = sqlite3.connect(SIGNALS_DB)
df_signals = pd.read_sql_query(
    "SELECT symbol, signal FROM trendline_signals",  # Güncellendi
    conn_sig
)
conn_sig.close()

# 5) AL ve SAT listelerini oluştur
groups = (
    df_signals
    .dropna(subset=["signal"])
    .groupby("signal")["symbol"]
    .unique()
)

# 6) Sonuç veritabanını oluştur
conn_res = sqlite3.connect(RESULTS_DB)
cur = conn_res.cursor()
cur.execute("DROP TABLE IF EXISTS list_returns;")
cur.execute("""
    CREATE TABLE list_returns (
        date TEXT,
        list_name TEXT,
        daily_return REAL
    );
""")
conn_res.commit()

# 7) Her liste için günlük ortalama getirileri hesapla ve yaz
for sig, symbols in groups.items():
    list_name = f"trendline_{sig.lower()}"  # "trendline_buy" veya "trendline_sell"

    df_sub = df_prices[df_prices["symbol"].isin(symbols)]
    if df_sub.empty:
        continue

    df_ret = (
        df_sub
        .groupby("date")["daily_return"]
        .mean()
        .reset_index()
        .assign(list_name=list_name)
    )

    df_ret.to_sql("list_returns", conn_res, if_exists="append", index=False)

conn_res.close()

print("✅ Trendline listeleri için günlük getiriler hesaplandı ve trendline_results.db’ye kaydedildi.")
