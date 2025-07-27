import sqlite3
import pandas as pd
from datetime import date

RESULTS_DB = "C:/Users/alper/Desktop/crew-investing/server/trendline_results.db"

def get_all_trendline_performance():
    # Veritabanından günlük getirileri oku
    conn = sqlite3.connect(RESULTS_DB)
    df = pd.read_sql_query(
        "SELECT date, list_name, daily_return FROM list_returns",
        conn,
        parse_dates=["date"]
    )
    conn.close()

    out = []
    for list_name, grp in df.groupby("list_name"):
        grp = grp.sort_values("date").copy()

        # SELL listeleri için işareti ters çevir
        if list_name.lower().endswith("_sell"):
            grp["adj_return"] = -grp["daily_return"]
        else:
            grp["adj_return"] = grp["daily_return"]

        last_date = grp["date"].max()

        # a) Günlük getiri
        daily = grp.loc[grp["date"] == last_date, "adj_return"].iloc[0]

        # b) Haftalık getiri (bileşik)
        week_df = grp[grp["date"] >= last_date - pd.Timedelta(days=7)]
        weekly = (week_df["adj_return"] + 1).prod() - 1 if not week_df.empty else 0

        # c) Aylık getiri (bileşik)
        month_df = grp[grp["date"] >= last_date - pd.Timedelta(days=30)]
        monthly = (month_df["adj_return"] + 1).prod() - 1 if not month_df.empty else 0

        # d) Tüm zamanlar
        all_time = (grp["adj_return"] + 1).prod() - 1

        out.append({
            "list_name": list_name,
            "as_of": str(last_date.date()),
            "daily": round(daily, 6),
            "weekly": round(weekly, 6),
            "monthly": round(monthly, 6),
            "all_time": round(all_time, 6)
        })

    return out


if __name__ == "__main__":
    for perf in get_all_trendline_performance():
        print(perf)
