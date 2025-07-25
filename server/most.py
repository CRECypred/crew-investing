import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from typing import Tuple
import warnings
warnings.filterwarnings('ignore')

class MOSTScreener:
    def __init__(self, length: int = 3, stop_loss_percent: float = 2.0, ma_type: str = "VAR"):
        self.length = length
        self.stop_loss_percent = stop_loss_percent
        self.ma_type = ma_type
        self.tillson_factor = 0.7

    def sma(self, data, period): return data.rolling(window=period).mean()
    def ema(self, data, period): return data.ewm(span=period).mean()

    def wma(self, data, period):
        weights = np.arange(1, period + 1)
        return data.rolling(window=period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

    def dema(self, data, period):
        ema1 = self.ema(data, period)
        ema2 = self.ema(ema1, period)
        return 2 * ema1 - ema2

    def tma(self, data, period):
        first_sma = self.sma(data, int(np.ceil(period / 2)))
        return self.sma(first_sma, int(np.floor(period / 2)) + 1)

    def var_ma(self, data, period):
        alpha = 2 / (period + 1)
        diff = data.diff().values.flatten()  # düzleştir
        up = pd.Series(np.where(diff > 0, diff, 0), index=data.index)
        down = pd.Series(np.where(diff < 0, -diff, 0), index=data.index)

        up_sum = up.rolling(window=9).sum()
        down_sum = down.rolling(window=9).sum()
        cmo = (up_sum - down_sum) / (up_sum + down_sum)
        cmo = cmo.fillna(0)

        var_ma = pd.Series(index=data.index, dtype=float)
        var_ma.iloc[0] = data.iloc[0]
        for i in range(1, len(data)):
            var_ma.iloc[i] = (alpha * abs(cmo.iloc[i]) * data.iloc[i] +
                              (1 - alpha * abs(cmo.iloc[i])) * var_ma.iloc[i - 1])
        return var_ma

    def wwma(self, data, period):
        alpha = 1 / period
        wwma = pd.Series(index=data.index, dtype=float)
        wwma.iloc[0] = data.iloc[0]
        for i in range(1, len(data)):
            wwma.iloc[i] = alpha * data.iloc[i] + (1 - alpha) * wwma.iloc[i - 1]
        return wwma

    def zlema(self, data, period):
        lag = period // 2 if period % 2 == 0 else (period - 1) // 2
        zlema_data = 2 * data - data.shift(lag)
        return self.ema(zlema_data, period)

    def tsf(self, data, period):
        def linear_regression(y):
            x = np.arange(len(y))
            if len(y) < 2:
                return 0, y[-1] if len(y) > 0 else 0
            slope = (len(y) * np.sum(x * y) - np.sum(x) * np.sum(y)) / (len(y) * np.sum(x**2) - np.sum(x)**2)
            intercept = (np.sum(y) - slope * np.sum(x)) / len(y)
            return slope, intercept

        tsf_values = []
        for i in range(len(data)):
            if i < period - 1:
                tsf_values.append(np.nan)
            else:
                y = data.iloc[i - period + 1:i + 1].values
                slope, intercept = linear_regression(y)
                tsf_values.append(intercept + slope * period)
        return pd.Series(tsf_values, index=data.index)

    def hull_ma(self, data, period):
        wma_half = self.wma(data, period // 2)
        wma_full = self.wma(data, period)
        raw = 2 * wma_half - wma_full
        return self.wma(raw, int(np.sqrt(period)))

    def tillson_t3(self, data, period, v=0.7):
        c1 = -v**3
        c2 = 3 * v**2 + 3 * v**3
        c3 = -6 * v**2 - 3 * v - 3 * v**3
        c4 = 1 + 3 * v + v**3 + 3 * v**2
        e1 = self.ema(data, period)
        e2 = self.ema(e1, period)
        e3 = self.ema(e2, period)
        e4 = self.ema(e3, period)
        e5 = self.ema(e4, period)
        e6 = self.ema(e5, period)
        return c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3

    def get_ma(self, data, period, ma_type):
        ma_map = {
            "SMA": self.sma,
            "EMA": self.ema,
            "WMA": self.wma,
            "DEMA": self.dema,
            "TMA": self.tma,
            "VAR": self.var_ma,
            "WWMA": self.wwma,
            "ZLEMA": self.zlema,
            "TSF": self.tsf,
            "HULL": self.hull_ma,
            "TILL": lambda d, p: self.tillson_t3(d, p, self.tillson_factor)
        }
        return ma_map.get(ma_type, self.var_ma)(data, period)

    def calculate_most(self, data: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        ma = self.get_ma(data, self.length, self.ma_type)
        stop_dist = ma * self.stop_loss_percent / 100
        long_stop = ma - stop_dist
        short_stop = ma + stop_dist

        long_adj = pd.Series(index=data.index, dtype=float)
        short_adj = pd.Series(index=data.index, dtype=float)
        direction = pd.Series(index=data.index, dtype=int)
        most_line = pd.Series(index=data.index, dtype=float)

        long_adj.iloc[0] = long_stop.iloc[0]
        short_adj.iloc[0] = short_stop.iloc[0]
        direction.iloc[0] = 1
        most_line.iloc[0] = long_adj.iloc[0]

        for i in range(1, len(data)):
            long_adj.iloc[i] = max(long_stop.iloc[i], long_adj.iloc[i-1]) if ma.iloc[i] > long_adj.iloc[i-1] else long_stop.iloc[i]
            short_adj.iloc[i] = min(short_stop.iloc[i], short_adj.iloc[i-1]) if ma.iloc[i] < short_adj.iloc[i-1] else short_stop.iloc[i]

            if direction.iloc[i-1] == -1 and ma.iloc[i] > short_adj.iloc[i-1]:
                direction.iloc[i] = 1
            elif direction.iloc[i-1] == 1 and ma.iloc[i] < long_adj.iloc[i-1]:
                direction.iloc[i] = -1
            else:
                direction.iloc[i] = direction.iloc[i-1]

            most_line.iloc[i] = long_adj.iloc[i] if direction.iloc[i] == 1 else short_adj.iloc[i]

        signals = direction.diff()
        return most_line, direction, signals, ma


