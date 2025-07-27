from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import logging
import pandas as pd
import numpy as np
import sqlite3
from most import MOSTScreener
from auth import auth_bp
from ma_lists import get_latest_signals
from performance import get_all_list_performance
from macd_lists import get_latest_macd_signals
from macd_performance import get_all_macd_performance
from trendline_performance import get_all_trendline_performance
from most_performance import get_all_most_performance
from most_ema_performance import get_all_most_ema_performance
import hashlib
import os


TRENDLINE_DB = "C:/Users/alper/Desktop/crew-investing/server/trendline_signals.db"


# 🔇 Flask loglarını azalt




app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.register_blueprint(auth_bp)



symbols_df = pd.read_csv("bist_symbols.csv")

symbols = {
    'XU100.IS': 'BIST 100',
    'XU030.IS': 'BIST 30',
    'USDTRY=X': 'Dolar/TL',
    'EURTRY=X': 'Euro/TL',
}

turkey_tz = pytz.timezone('Europe/Istanbul')

@app.route("/api/ma-last-signals-8-22")
def get_ma_last_signals_8_22():
    try:
        conn = sqlite3.connect("signals.db")
        df = pd.read_sql_query("""
            SELECT * FROM ma_signals
            WHERE short_window = 8 AND long_window = 22
        """, conn)
        conn.close()
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        print("MA(8/22) API HATASI:", e)
        return jsonify([]), 500


@app.route("/api/ma-last-signals-22-50")
def get_ma_last_signals_22_50():
    try:
        conn = sqlite3.connect("signals.db")
        df = pd.read_sql_query("""
            SELECT * FROM ma_signals
            WHERE short_window = 22 AND long_window = 50
        """, conn)
        conn.close()
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        print("MA(22/50) API HATASI:", e)
        return jsonify([]), 500


@app.route("/api/ma-last-signals-50-200")
def get_ma_last_signals_50_200():
    try:
        conn = sqlite3.connect("signals.db")
        df = pd.read_sql_query("""
            SELECT * FROM ma_signals
            WHERE short_window = 50 AND long_window = 200
        """, conn)
        conn.close()
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        print("MA(50/200) API HATASI:", e)
        return jsonify([]), 500


@app.route("/api/list-performance")
def list_performance():
    try:
        data = get_all_list_performance()
        return jsonify(data)
    except Exception as e:
        # Hata olursa ayrıntıyı döner
        return jsonify({"error": str(e)}), 500

@app.route("/api/macd-last-buy-signals")
def get_macd_last_buy_signals():
    try:
        all_signals = get_latest_macd_signals()
        buy_signals = [s for s in all_signals if s["signal"] == "AL"]
        return jsonify(buy_signals)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/macd-last-sell-signals")
def get_macd_last_sell_signals():
    try:
        all_signals = get_latest_macd_signals()
        sell_signals = [s for s in all_signals if s["signal"] == "SAT"]
        return jsonify(sell_signals)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/macd-performance")
def macd_performance():
    try:
        data = get_all_macd_performance()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/most-ema-last-buy-signals")
def most_ema_last_buy_signals():
    try:
        conn = sqlite3.connect("most_ema_signals.db")
        df = pd.read_sql_query("SELECT * FROM most_ema_signals WHERE signal = 'BUY'", conn)
        conn.close()
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        print("MOST EMA BUY SELECT HATASI:", e)
        return jsonify([]), 500


@app.route("/api/most-ema-last-sell-signals")
def most_ema_last_sell_signals():
    try:
        conn = sqlite3.connect("most_ema_signals.db")
        df = pd.read_sql_query("SELECT * FROM most_ema_signals WHERE signal = 'SELL'", conn)
        conn.close()
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        print("MOST EMA SELL SELECT HATASI:", e)
        return jsonify([]), 500

@app.route("/api/most-ema-performance")
def most_ema_performance():
    try:
        performance = get_all_most_ema_performance()
        return jsonify(performance)
    except Exception as e:
        print("MOST EMA PERFORMANCE HATASI:", e)
        return jsonify([]), 500

@app.route("/api/oldschool-last-buy-signals")
def oldschool_last_buy():
    try:
        conn = sqlite3.connect("C:/Users/alper/Desktop/crew-investing/server/oldschool_signals.db")
        df = pd.read_sql_query("SELECT * FROM oldschool_signals WHERE signal = 'BUY'", conn)
        conn.close()
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        print("Oldschool BUY HATASI:", e)
        return jsonify([]), 500

@app.route("/api/oldschool-last-sell-signals")
def oldschool_last_sell():
    try:
        conn = sqlite3.connect("C:/Users/alper/Desktop/crew-investing/server/oldschool_signals.db")
        df = pd.read_sql_query("SELECT * FROM oldschool_signals WHERE signal = 'SELL'", conn)
        conn.close()
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        print("Oldschool SELL HATASI:", e)
        return jsonify([]), 500

@app.route("/api/oldschool-performance")
def oldschool_performance():
    try:
        from oldschool_performance import get_all_oldschool_performance
        return jsonify(get_all_oldschool_performance())
    except Exception as e:
        print("Oldschool Performans HATASI:", e)
        return jsonify([]), 500


@app.route('/api/trendline-last-buy-signals')
def get_trendline_buy_signals():
    conn = sqlite3.connect(TRENDLINE_DB)
    df = pd.read_sql_query("SELECT * FROM trendline_signals WHERE signal='BUY'", conn)
    conn.close()
    df.sort_values("date", ascending=False, inplace=True)
    return jsonify(df.to_dict(orient="records"))

@app.route('/api/trendline-last-sell-signals')
def get_trendline_sell_signals():
    conn = sqlite3.connect(TRENDLINE_DB)
    df = pd.read_sql_query("SELECT * FROM trendline_signals WHERE signal='SELL'", conn)
    conn.close()
    df.sort_values("date", ascending=False, inplace=True)
    return jsonify(df.to_dict(orient="records"))

@app.route("/api/trendline-performance")
def trendline_performance():
    try:
        data = get_all_trendline_performance()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/most-last-buy-signals")
def most_last_buy_signals():
    conn = sqlite3.connect("most_signals.db")
    df = pd.read_sql_query("SELECT * FROM most_signals WHERE signal = 'BUY'", conn)
    conn.close()
    return jsonify(df.to_dict(orient="records"))

@app.route("/api/most-last-sell-signals")
def most_last_sell_signals():
    conn = sqlite3.connect("most_signals.db")
    df = pd.read_sql_query("SELECT * FROM most_signals WHERE signal = 'SELL'", conn)
    conn.close()
    return jsonify(df.to_dict(orient="records"))

@app.route("/api/most-performance")
def most_performance():
    data = get_all_most_performance()
    return jsonify(data)

@app.route("/api/most/<symbol>")
def get_most_data(symbol):
    df = yf.download(symbol, period="12mo", interval="1d")
    close = df["Close"]

    most = MOSTScreener(length=3, stop_loss_percent=2.0, ma_type="VAR")
    most_line, direction, signals, ma = most.calculate_most(close)

    result = []
    for i in range(len(df)):
        result.append({
            "time": df.index[i].strftime("%Y-%m-%d"),
            "most": round(most_line.iloc[i], 2) if not pd.isna(most_line.iloc[i]) else None,
            "ma": round(ma.iloc[i], 2) if not pd.isna(ma.iloc[i]) else None,
            "signal": "buy" if signals.iloc[i] == 2 else "sell" if signals.iloc[i] == -2 else None
        })

    return jsonify(result)


@app.route("/api/fundamentals/<symbol>")
def get_fundamentals(symbol):
    import yfinance as yf
    import traceback

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        fundamentals = {
            "pe": info.get("trailingPE"),
            "pb": info.get("priceToBook"),
            "roe": info.get("returnOnEquity"),
            "eps": info.get("trailingEps"),
            "profitMargin": info.get("profitMargins"),
            "netIncome": info.get("netIncomeToCommon"),
            "revenue": info.get("totalRevenue"),
            "bookValue": info.get("bookValue"),
            "beta": info.get("beta"),
            "sector": info.get("sector"),
        }

        labels_tr = {
            "pe": "Fiyat/Kazanç (F/K)",
            "pb": "PD/DD (Fiyat/Defter)",
            "roe": "Özsermaye Karlılığı (ROE)",
            "eps": "Hisse Başına Kar (EPS)",
            "profitMargin": "Net Kar Marjı",
            "netIncome": "Net Kar",
            "revenue": "Toplam Gelir",
            "bookValue": "Özsermaye",
            "beta": "Beta",
            "sector": "Sektör"
        }

        # Sadece geçerli (None olmayan ve sayısal ya da string olan) değerleri dahil et
        result = [
            {"key": k, "label": labels_tr.get(k, k), "value": fundamentals[k]}
            for k in fundamentals
            if fundamentals[k] not in [None, ""]  # boş olanları çıkar
        ]

        return jsonify(result)

    except Exception as e:
        print("FUNDAMENTALS HATASI:\n", traceback.format_exc())
        return jsonify({"error": str(e)}), 500


def get_real_prev_close_hourly(symbol):
    try:
        now = datetime.now(tz=turkey_tz)
        yesterday = now - timedelta(days=1)
        start_str = yesterday.strftime('%Y-%m-%d')
        df = yf.download(symbol, start=start_str, interval='1h', auto_adjust=False, progress=False)
        if df.empty:
            return None
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC').tz_convert('Europe/Istanbul')
        else:
            df.index = df.index.tz_convert('Europe/Istanbul')
        df_window = df.between_time('23:00', '23:59')
        if not df_window.empty:
            return df_window['Close'].iloc[-1].item()
        else:
            return None
    except Exception:
        return None


@app.route('/api/prices')
def get_prices():
    results = []
    for symbol, name in symbols.items():
        try:
            df = yf.download(symbol, period='6d', interval='1d', auto_adjust=False, progress=False)
            if df.empty or len(df) < 2:
                continue
            today_row = df.iloc[-1]
            open_price = today_row['Open'].item()
            close_price = today_row['Close'].item()
            if symbol in ['USDTRY=X', 'EURTRY=X']:
                real_prev_close = get_real_prev_close_hourly(symbol)
                if real_prev_close is None:
                    real_prev_close = df.iloc[-2]['Close'].item()
            else:
                real_prev_close = df.iloc[-2]['Close'].item()
            change = close_price - real_prev_close
            change_percent = (change / real_prev_close) * 100
            results.append({
                'symbol': symbol,
                'name': name,
                'open': round(open_price, 4),
                'current': round(close_price, 4),
                'change': round(change, 4),
                'change_percent': round(change_percent, 2)
            })
        except Exception:
            continue
    return jsonify(results)


@app.route('/api/chart/<symbol>')
def get_chart_data(symbol):
    try:
        end_date = datetime.today() + timedelta(days=1)
        start_date = end_date - timedelta(days=700)
        df = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'),
                         end=end_date.strftime('%Y-%m-%d'), interval='1d',
                         auto_adjust=False, progress=False)
        if df.empty:
            return jsonify({'error': 'Veri bulunamadı'}), 404
        df = df.tail(700)
        data = []
        for date, row in df.iterrows():
            try:
                data.append({
                    'time': date.to_pydatetime().strftime('%Y-%m-%d'),
                    'open': round(row['Open'].item(), 2),
                    'high': round(row['High'].item(), 2),
                    'low': round(row['Low'].item(), 2),
                    'close': round(row['Close'].item(), 2)
                })
            except:
                continue
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/symbols')
def get_symbols():
    query = request.args.get('q', '').upper()
    if not query:
        return jsonify([])
    matches = symbols_df[symbols_df['Symbol'].str.startswith(query, na=False)]
    return jsonify(matches['Symbol'].dropna().head(10).tolist())


@app.route('/api/trendlines/<symbol>')
def get_trendlines(symbol):
    try:
        df = yf.download(symbol, interval='1d', period='700d', auto_adjust=False, progress=False)
        if df.empty:
            return jsonify({'error': 'Veri bulunamadı'}), 404

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [col.lower() for col in df.columns]

        df = df[['open', 'high', 'low', 'close']]
        df.reset_index(inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        data = df.tail(700).copy()

        lookback = 30
        segments = []
        breakpoints = []

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

        i = 0
        while i + lookback < len(data):
            w = data.iloc[i:i + lookback]
            sup_coef, res_coef = fit_trendlines(w['high'].values, w['low'].values, w['close'].values)
            seg = data.iloc[i:i + lookback]

            if i + lookback < len(data):
                next_close = data.iloc[i + lookback]['close']
                next_date = data.index[i + lookback]
                sup_val = sup_coef[0] * lookback + sup_coef[1]
                res_val = res_coef[0] * lookback + res_coef[1]

                if next_close < sup_val * 0.995:
                    breakpoints.append({
                        "date": next_date.strftime('%Y-%m-%d'),
                        "price": round(next_close, 2),
                        "type": "SELL"
                    })
                    i += lookback
                    continue

                if next_close > res_val * 1.005:
                    breakpoints.append({
                        "date": next_date.strftime('%Y-%m-%d'),
                        "price": round(next_close, 2),
                        "type": "BUY"
                    })
                    i += lookback
                    continue

            segment = {
                'dates': [d.strftime('%Y-%m-%d') for d in seg.index],
                'support': [round(sup_coef[0]*j + sup_coef[1], 2) for j in range(len(seg))],
                'resistance': [round(res_coef[0]*j + res_coef[1], 2) for j in range(len(seg))]
            }
            segments.append(segment)
            i += 1

        return jsonify({
            "segments": segments,
            "breaks": breakpoints
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ma-signals/<symbol>')
def get_ma_signals(symbol):
    try:
        df = yf.download(symbol, period='200d', interval='1d', auto_adjust=False, progress=False)
        if df.empty:
            return jsonify({'error': 'Veri bulunamadı'}), 404

        df.reset_index(inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        df.columns = [
            col.lower().split('_')[0] if isinstance(col, str)
            else '_'.join(col).lower().split('_')[0]
            for col in df.columns
        ]

        df['ma8'] = df['close'].rolling(window=8).mean()
        df['ma22'] = df['close'].rolling(window=22).mean()
        df.dropna(subset=['close', 'ma8', 'ma22'], inplace=True)

        df['signal'] = np.where(df['ma8'] > df['ma22'], 1, 0)
        df['position'] = df['signal'].diff()

        ma8 = [{'date': d.strftime('%Y-%m-%d'), 'value': round(v, 2)} for d, v in df['ma8'].items()]
        ma22 = [{'date': d.strftime('%Y-%m-%d'), 'value': round(v, 2)} for d, v in df['ma22'].items()]

        signals = []
        for date, row in df.iterrows():
            if row['position'] == 1:
                signals.append({'date': date.strftime('%Y-%m-%d'), 'price': round(row['close'], 2), 'type': 'BUY'})
            elif row['position'] == -1:
                signals.append({'date': date.strftime('%Y-%m-%d'), 'price': round(row['close'], 2), 'type': 'SELL'})

        return jsonify({
            'ma8': ma8,
            'ma22': ma22,
            'signals': signals
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ma-midsignals/<symbol>')
def get_ma_signals_22_50(symbol):
    try:
        df = yf.download(symbol, period='300d', interval='1d', auto_adjust=False, progress=False)
        if df.empty:
            return jsonify({'error': 'Veri bulunamadı'}), 404

        df.reset_index(inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        df.columns = [
            col.lower().split('_')[0] if isinstance(col, str)
            else '_'.join(col).lower().split('_')[0]
            for col in df.columns
        ]

        df['ma22'] = df['close'].rolling(window=22).mean()
        df['ma50'] = df['close'].rolling(window=50).mean()
        df.dropna(subset=['close', 'ma22', 'ma50'], inplace=True)

        df['signal'] = np.where(df['ma22'] > df['ma50'], 1, 0)
        df['position'] = df['signal'].diff()

        ma22 = [{'date': d.strftime('%Y-%m-%d'), 'value': round(v, 2)} for d, v in df['ma22'].items()]
        ma50 = [{'date': d.strftime('%Y-%m-%d'), 'value': round(v, 2)} for d, v in df['ma50'].items()]

        signals = []
        for date, row in df.iterrows():
            if row['position'] == 1:
                signals.append({'date': date.strftime('%Y-%m-%d'), 'price': round(row['close'], 2), 'type': 'BUY'})
            elif row['position'] == -1:
                signals.append({'date': date.strftime('%Y-%m-%d'), 'price': round(row['close'], 2), 'type': 'SELL'})

        return jsonify({
            'ma22': ma22,
            'ma50': ma50,
            'signals': signals
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ma-signals-50-200/<symbol>')
def get_ma_signals_50_200(symbol):
    try:
        df = yf.download(symbol, period='400d', interval='1d', auto_adjust=False, progress=False)
        if df.empty:
            return jsonify({'error': 'Veri bulunamadı'}), 404

        df.reset_index(inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        df.columns = [
            col.lower().split('_')[0] if isinstance(col, str)
            else '_'.join(col).lower().split('_')[0]
            for col in df.columns
        ]

        df['ma50'] = df['close'].rolling(window=50).mean()
        df['ma200'] = df['close'].rolling(window=200).mean()
        df.dropna(subset=['close', 'ma50', 'ma200'], inplace=True)

        df['signal'] = np.where(df['ma50'] > df['ma200'], 1, 0)
        df['position'] = df['signal'].diff()

        ma50 = [{'date': d.strftime('%Y-%m-%d'), 'value': round(v, 2)} for d, v in df['ma50'].items()]
        ma200 = [{'date': d.strftime('%Y-%m-%d'), 'value': round(v, 2)} for d, v in df['ma200'].items()]

        signals = []
        for date, row in df.iterrows():
            if row['position'] == 1:
                signals.append({'date': date.strftime('%Y-%m-%d'), 'price': round(row['close'], 2), 'type': 'BUY'})
            elif row['position'] == -1:
                signals.append({'date': date.strftime('%Y-%m-%d'), 'price': round(row['close'], 2), 'type': 'SELL'})

        return jsonify({
            'ma50': ma50,
            'ma200': ma200,
            'signals': signals
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/most-ema/<symbol>")
def get_most_ema(symbol):
    try:
        df = yf.download(symbol, period="12mo", interval="1d", auto_adjust=False, progress=False)
        if df.empty:
            return jsonify({'error': 'Veri bulunamadı'}), 404

        # Çoklu kolon varsa dümdüzleştir
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        if "Close" not in df.columns:
            return jsonify({'error': '"Close" kolonu bulunamadı'}), 500

        close = df["Close"]

        most = MOSTScreener(length=3, stop_loss_percent=2.0, ma_type="EMA")
        most_line, direction, signals, ma = most.calculate_most(close)

        result = []
        for i in range(len(df)):
            result.append({
                "time": df.index[i].strftime("%Y-%m-%d"),
                "most": round(most_line.iloc[i], 2) if not pd.isna(most_line.iloc[i]) else None,
                "ma": round(ma.iloc[i], 2) if not pd.isna(ma.iloc[i]) else None,
                "signal": "buy" if signals.iloc[i] == 2 else "sell" if signals.iloc[i] == -2 else None
            })

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/summary/<symbol>')
def get_summary(symbol):
    import yfinance as yf

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="5d", interval="1d")
        if df.empty or len(df) < 2:
            return jsonify({"error": "Yeterli veri yok"}), 400

        current = float(df['Close'].iloc[-1])
        previous = float(df['Close'].iloc[-2])
        change_amount = current - previous
        change_percent = ((current - previous) / previous) * 100

        # İngilizce → Türkçe sektör eşlemesi
        sector_map = {
            "Technology": "Teknoloji",
            "Healthcare": "Sağlık",
            "Financial Services": "Finansal Hizmetler",
            "Consumer Cyclical": "Tüketici Döngüsel",
            "Consumer Defensive": "Tüketici Savunma",
            "Utilities": "Kamu Hizmetleri",
            "Industrials": "Sanayi",
            "Basic Materials": "Hammadde",
            "Energy": "Enerji",
            "Real Estate": "Gayrimenkul",
            "Communication Services": "İletişim Hizmetleri"
        }

        info = ticker.info
        name = info.get("shortName") or info.get("longName") or symbol

        # Sektör verisini güvenli şekilde al
        sector_raw = info.get("sector")


        sector_clean = (sector_raw or "Bilinmiyor").strip().lower()
        sector_tr = next(
            (val for key, val in sector_map.items() if key.lower() == sector_clean),
            sector_raw or "Bilinmiyor"
        )

        volume = info.get("volume") or info.get("regularMarketVolume") or 0

        return jsonify({
            "symbol": symbol.upper(),
            "name": name,
            "price": round(current, 2),
            "changePercent": round(change_percent, 2),
            "changeAmount": round(change_amount, 2),
            "currency": "TRY",
            "sector": sector_tr,
            "volume": int(volume),
            "closeTime": "18:10"  # BIST varsayılan kapanış saati
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route("/api/macd/<symbol>")
def get_macd(symbol):
    try:
        df = yf.download(symbol, period="200d", interval="1d", auto_adjust=False)
        if df.empty:
            return jsonify({'error': 'Veri bulunamadı'}), 404

        df.reset_index(inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        # 👇 Burada tuple hatası çözülüyor
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [col.lower() for col in df.columns]

        if 'close' not in df.columns:
            return jsonify({'error': '"close" kolonu bulunamadı'}), 500

        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal

        df['macd'] = macd
        df['signal'] = signal
        df['hist'] = hist

        df['macd_signal'] = np.where(df['macd'] > df['signal'], 1, 0)
        df['position'] = df['macd_signal'].diff()

        result = []
        for date, row in df.iterrows():
            item = {
                "time": date.strftime("%Y-%m-%d"),
                "macd": round(row['macd'], 4) if not pd.isna(row['macd']) else None,
                "signal": round(row['signal'], 4) if not pd.isna(row['signal']) else None,
                "hist": round(row['hist'], 4) if not pd.isna(row['hist']) else None,
                "price": round(row['close'], 2) if not pd.isna(row['close']) else None,
                "signal_type": "buy" if row['position'] == 1 else ("sell" if row['position'] == -1 else None)
            }
            result.append(item)

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/list-status/<symbol>")
def get_list_status(symbol):
    import sqlite3
    import pandas as pd

    symbol = symbol.upper()
    result = {}

    # --- MA kontrolü (ma_signals tablosu)
    def check_ma_signal(symbol, short, long, target_signal):
        try:
            conn = sqlite3.connect("signals.db")
            df = pd.read_sql_query(
                """
                SELECT symbol FROM ma_signals
                WHERE symbol = ?
                AND short_window = ?
                AND long_window = ?
                AND signal = ?
                """,
                conn,
                params=(symbol, short, long, target_signal),
            )
            conn.close()
            return not df.empty
        except Exception as e:
            print(f"MA {short}/{long} kontrol hatası:", e)
            return False

    for short, long in [(8, 22), (22, 50), (50, 200)]:
        label = f"ma_{short}_{long}"
        is_buy = check_ma_signal(symbol, short, long, "AL")
        is_sell = check_ma_signal(symbol, short, long, "SAT")
        result[label] = "buy" if is_buy else "sell" if is_sell else "none"

    # --- MACD kontrolü (macd_signals tablosu)
    def check_macd_signal(symbol, signal_type):
        try:
            conn = sqlite3.connect("macd_signals.db")
            df = pd.read_sql_query(
                "SELECT symbol FROM macd_signals WHERE symbol = ? AND signal = ?",
                conn,
                params=(symbol, signal_type)
            )
            conn.close()
            return not df.empty
        except Exception as e:
            print("MACD kontrol hatası:", e)
            return False

    result["macd"] = (
        "buy" if check_macd_signal(symbol, "AL")
        else "sell" if check_macd_signal(symbol, "SAT")
        else "none"
    )

    # --- MOST EMA kontrolü (most_ema_signals tablosu)
    def check_most_ema_signal(symbol, signal_type):
        try:
            conn = sqlite3.connect("most_ema_signals.db")
            df = pd.read_sql_query(
                "SELECT symbol FROM most_ema_signals WHERE symbol = ? AND signal = ?",
                conn,
                params=(symbol, signal_type)
            )
            conn.close()
            return not df.empty
        except Exception as e:
            print("MOST EMA kontrol hatası:", e)
            return False

    result["most_ema"] = (
        "buy" if check_most_ema_signal(symbol, "BUY")
        else "sell" if check_most_ema_signal(symbol, "SELL")
        else "none"
    )

    return jsonify({
        "symbol": symbol,
        "statuses": result
    })

@app.route("/api/comments/<symbol>")
def get_comments(symbol):
    # --- Kullanıcı rolleri için users.db
    conn_users = sqlite3.connect("users.db")
    cursor_users = conn_users.cursor()
    cursor_users.execute("SELECT username, role FROM users")
    user_roles = dict(cursor_users.fetchall())
    conn_users.close()

    # --- Yorumlar için comments.db
    conn = sqlite3.connect("comments.db")
    cursor = conn.cursor()

    # Tüm yorumları çek
    cursor.execute("SELECT * FROM comments WHERE symbol = ? ORDER BY timestamp ASC", (symbol,))
    rows = cursor.fetchall()

    # Beğenenleri ve yanıtları ayırmak için
    comment_map = {}
    for row in rows:
        comment_id = row[0]
        cursor.execute("SELECT username FROM likes WHERE comment_id = ?", (comment_id,))
        likers = [r[0] for r in cursor.fetchall()]

        username = row[2]
        comment = {
            "id": comment_id,
            "symbol": row[1],
            "username": username,
            "comment": row[3],
            "timestamp": row[4],
            "likes": row[5],
            "parent_id": row[6],
            "likers": likers,
            "role": user_roles.get(username, "user"),  # Default: user
            "replies": [],
        }
        comment_map[comment_id] = comment

    # Yanıtları ana yorumlara ekle
    top_level_comments = []
    for comment in comment_map.values():
        if comment["parent_id"]:
            parent = comment_map.get(comment["parent_id"])
            if parent:
                parent["replies"].append(comment)
        else:
            top_level_comments.append(comment)

    conn.close()
    return jsonify(top_level_comments)




@app.route("/api/comments/<symbol>", methods=["POST"])
def post_comment(symbol):
    data = request.get_json()
    username = data.get("username")
    comment = data.get("comment")
    parent_id = data.get("parent_id", None)

    if not username or not comment:
        return jsonify({"error": "Eksik veri"}), 400

    conn = sqlite3.connect("comments.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO comments (symbol, username, comment, parent_id) VALUES (?, ?, ?, ?)",
        (symbol.upper(), username, comment, parent_id)
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route("/api/comments/<symbol>/<int:comment_id>", methods=["DELETE"])
def delete_comment(symbol, comment_id):
    data = request.get_json()
    username = data.get("username")

    if not username:
        return jsonify({"error": "Kullanıcı adı gerekli"}), 400

    conn = sqlite3.connect("comments.db")
    cursor = conn.cursor()

    # Yorumu bul
    cursor.execute("SELECT username FROM comments WHERE id = ? AND symbol = ?", (comment_id, symbol))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Yorum bulunamadı."}), 404

    comment_owner = row[0]

    # Kullanıcının rolünü kontrol et (admin veya mod ise herkesin yorumunu silebilir)
    conn_user = sqlite3.connect("users.db")
    cursor_user = conn_user.cursor()
    cursor_user.execute("SELECT role FROM users WHERE username = ?", (username,))
    user_row = cursor_user.fetchone()
    conn_user.close()

    if not user_row:
        conn.close()
        return jsonify({"error": "Kullanıcı bulunamadı."}), 404

    role = user_row[0]

    if username != comment_owner and role not in ("admin", "mod"):
        conn.close()
        return jsonify({"error": "Bu yorumu silme yetkiniz yok."}), 403

    # Yorum sil
    cursor.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    full_name = data.get("full_name")
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    if not all([full_name, email, username, password]):
        return jsonify({"error": "Tüm alanlar zorunludur"}), 400

    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Kullanıcı zaten var mı kontrol et
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": "Bu kullanıcı adı zaten alınmış"}), 400

        # Yeni kullanıcıyı ekle
        cursor.execute("""
            INSERT INTO users (full_name, email, username, password, role)
            VALUES (?, ?, ?, ?, 'user')
        """, (full_name, email, username, password))

        conn.commit()
        conn.close()
        return jsonify({"success": True}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/user/<username>")
def get_user_info(username):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, email, username, role FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return jsonify({
                "full_name": row[0],
                "email": row[1],
                "username": row[2],
                "role": row[3],
            })
        else:
            return jsonify({"error": "Kullanıcı bulunamadı"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Kullanıcı adı ve şifre zorunlu"}), 400

    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, password, role FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        conn.close()

        if not user:
            return jsonify({"error": "Kullanıcı bulunamadı"}), 404

        db_password = user[1]
        role = user[2]

        if password != db_password:
            return jsonify({"error": "Hatalı şifre"}), 401

        return jsonify({
            "success": True,
            "username": username,
            "role": role
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/change-password", methods=["POST"])
def change_password():
    data = request.get_json()
    username = data.get("username")
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not all([username, old_password, new_password]):
        return jsonify({"error": "Tüm alanlar zorunludur"}), 400

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Kullanıcı bulunamadı"}), 404

    current_hashed = row[0]
    old_hashed = hashlib.sha256(old_password.encode()).hexdigest()

    if old_hashed != current_hashed:
        conn.close()
        return jsonify({"error": "Mevcut şifre yanlış"}), 401

    new_hashed = hashlib.sha256(new_password.encode()).hexdigest()
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_hashed, username))
    conn.commit()
    conn.close()

    return jsonify({"success": True})



@app.route("/api/comments/<symbol>/<int:comment_id>/like", methods=["POST"])
def toggle_like(symbol, comment_id):
    data = request.get_json()
    username = data.get("username")

    if not username:
        return jsonify({"error": "Kullanıcı adı gerekli"}), 400

    conn = sqlite3.connect("comments.db")
    cursor = conn.cursor()

    # Beğeni var mı kontrol et
    cursor.execute("SELECT 1 FROM likes WHERE comment_id = ? AND username = ?", (comment_id, username))
    liked = cursor.fetchone()

    if liked:
        # Zaten beğenmişse: geri çek
        cursor.execute("DELETE FROM likes WHERE comment_id = ? AND username = ?", (comment_id, username))
        cursor.execute("UPDATE comments SET likes = likes - 1 WHERE id = ?", (comment_id,))
    else:
        # Beğenmemişse: beğen
        cursor.execute("INSERT INTO likes (comment_id, username) VALUES (?, ?)", (comment_id, username))
        cursor.execute("UPDATE comments SET likes = likes + 1 WHERE id = ?", (comment_id,))

    conn.commit()
    conn.close()

    return jsonify({"success": True})











if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
