import pathway as pw
from collections import deque
from typing import Tuple, Optional, List, Iterable
from datetime import datetime


def safe_float(val, default=0.0):
    """Safely convert value to float with fallback."""
    try:
        if val is None:
            return default
        return float(val)
    except Exception:
        return default


class DequeAccumulatorBase(pw.BaseCustomAccumulator):
    """
    Base for accumulators whose state is one or more deque attributes.
    Subclasses must define ACC_FIELDS as a tuple of attribute names.
    """
    ACC_FIELDS: Tuple[str, ...] = ()

    def update(self, other: "DequeAccumulatorBase"):
        for name in self.ACC_FIELDS:
            getattr(self, name).extend(getattr(other, name))

    def retract(self, other: "DequeAccumulatorBase"):
        for name in self.ACC_FIELDS:
            src = getattr(self, name)
            for val in getattr(other, name):
                try:
                    src.remove(val)
                except ValueError:
                    # Ignore if not present, matching original behavior
                    pass


class DayChangeAccumulator(DequeAccumulatorBase):
    """Computes absolute change and percentage change since start of trading day."""
    ACC_FIELDS = ("data_points",)

    def __init__(self, data_points):
        # Store tuples of (date_string_or_datetime, price)
        self.data_points = deque(data_points)

    @classmethod
    def from_row(cls, row):
        try:
            d, c = row
            return cls([(d, c)])
        except (ValueError, TypeError):
            # Fallback if row format is unexpected
            return cls([row])

    def compute_result(self):
        if not self.data_points:
            return (0.0, 0.0)

        # Convert to list and sort by date
        sorted_data = sorted(self.data_points, key=lambda x: x[0])

        if len(sorted_data) < 1:
            return (0.0, 0.0)

        try:
            # Get the latest date and price
            latest_date_str, latest_price = sorted_data[-1]

            # Parse the latest date to get current day
            if isinstance(latest_date_str, str):
                if "T" in latest_date_str:
                    latest_date = datetime.fromisoformat(
                        latest_date_str.replace("+05:30", "+0530")
                    )
                else:
                    latest_date = datetime.strptime(
                        latest_date_str, "%Y-%m-%d %H:%M:%S"
                    )
            else:
                # Fallback if already datetime
                latest_date = latest_date_str

            current_day = latest_date.date()

            # Find the first price of the current day
            day_start_price = None
            for date_str, price in sorted_data:
                if isinstance(date_str, str):
                    if "T" in date_str:
                        date_obj = datetime.fromisoformat(
                            date_str.replace("+05:30", "+0530")
                        )
                    else:
                        date_obj = datetime.strptime(
                            date_str, "%Y-%m-%d %H:%M:%S"
                        )
                else:
                    date_obj = date_str

                if date_obj.date() == current_day:
                    day_start_price = price
                    break

            # Calculate absolute and percentage change
            if day_start_price is None or day_start_price == 0:
                return (0.0, 0.0)

            abs_change = latest_price - day_start_price
            pct_change = (abs_change / day_start_price) * 100

            return (round(abs_change, 2), round(pct_change, 2))

        except Exception:
            return (0.0, 0.0)


class MACDAccumulator(DequeAccumulatorBase):
    """Computes MACD, Signal, and Histogram."""
    ACC_FIELDS = ("prices",)

    def __init__(self, prices):
        self.prices = deque(prices)

    @classmethod
    def from_row(cls, row):
        return cls([row[0]])

    def compute_result(self):
        if not self.prices:
            return (0.0, 0.0, 0.0)

        def ema_stream(prices, span):
            if not prices:
                return []
            alpha = 2 / (span + 1)
            ema = prices[0]
            out = [ema]
            for price in list(prices)[1:]:
                ema = price * alpha + ema * (1 - alpha)
                out.append(ema)
            return out

        price_list = list(self.prices)
        ema12 = ema_stream(price_list, 12)
        ema26 = ema_stream(price_list, 26)
        if not ema12 or not ema26:
            return (0.0, 0.0, 0.0)

        macd_list = [e12 - e26 for e12, e26 in zip(ema12, ema26)]
        ema9 = ema_stream(macd_list, 9) if macd_list else [0.0]
        m = macd_list[-1] if macd_list else 0.0
        s = ema9[-1] if ema9 else 0.0
        return (m, s, m - s)


class RSIAccumulator(DequeAccumulatorBase):
    """Computes Relative Strength Index over 14 periods."""
    ACC_FIELDS = ("items",)

    def __init__(self, items):
        self.items = deque(items)

    @classmethod
    def from_row(cls, row):
        c, d = row
        return cls([(c, d)])

    def compute_result(self):
        items = sorted(self.items, key=lambda x: x[1])
        prices = [x[0] for x in items]
        if len(prices) < 2:
            return 50.0

        period = 14
        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        avg_gain = sum(max(d, 0) for d in deltas[:period]) / period
        avg_loss = sum(abs(min(d, 0)) for d in deltas[:period]) / period

        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * 13 + max(deltas[i], 0)) / 14
            avg_loss = (avg_loss * 13 + abs(min(deltas[i], 0))) / 14

        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))


class ADLAccumulator(DequeAccumulatorBase):
    """Accumulate/Distribution Line indicator."""
    ACC_FIELDS = ("highs", "lows", "closes", "volumes")

    def __init__(self, highs, lows, closes, volumes):
        self.highs = deque(highs)
        self.lows = deque(lows)
        self.closes = deque(closes)
        self.volumes = deque(volumes)

    @classmethod
    def from_row(cls, row):
        d, h, l, c, v = row
        return cls([(d, h)], [(d, l)], [(d, c)], [(d, v)])

    def compute_result(self):
        hd, ld, cd, vd = dict(self.highs), dict(self.lows), dict(self.closes), dict(self.volumes)
        dates = set(hd) & set(ld) & set(cd) & set(vd)
        adl = 0.0
        for dt in sorted(dates):
            h, l, c, v = hd[dt], ld[dt], cd[dt], vd[dt]
            denom = h - l if h != l else 1
            mfm = ((c - l) - (h - c)) / denom
            adl += mfm * v
        return adl


class SMA20Accumulator(DequeAccumulatorBase):
    """Simple Moving Average (20 periods)."""
    ACC_FIELDS = ("prices",)

    def __init__(self, prices):
        self.prices = deque(prices)

    @classmethod
    def from_row(cls, row):
        return cls([row[0]])

    def compute_result(self):
        if len(self.prices) < 20:
            return 0.0
        return sum(list(self.prices)[-20:]) / 20


class SMA50Accumulator(DequeAccumulatorBase):
    """Simple Moving Average (50 periods)."""
    ACC_FIELDS = ("prices",)

    def __init__(self, prices):
        self.prices = deque(prices)

    @classmethod
    def from_row(cls, row):
        return cls([row[0]])

    def compute_result(self):
        if len(self.prices) < 50:
            return 0.0
        return sum(list(self.prices)[-50:]) / 50


class Std20Accumulator(DequeAccumulatorBase):
    """Standard Deviation (20 periods)."""
    ACC_FIELDS = ("prices",)

    def __init__(self, prices):
        self.prices = deque(prices)

    @classmethod
    def from_row(cls, row):
        return cls([row[0]])

    def compute_result(self):
        if len(self.prices) < 20:
            return 0.0
        data = list(self.prices)[-20:]
        mean = sum(data) / 20
        var = sum((x - mean) ** 2 for x in data) / 20
        return var ** 0.5


class BollingerBand20Accumulator(DequeAccumulatorBase):
    """Bollinger Bands (20 periods, 2 std dev)."""
    ACC_FIELDS = ("prices",)

    def __init__(self, prices):
        self.prices = deque(prices)

    @classmethod
    def from_row(cls, row):
        return cls([row[0]])

    def compute_result(self):
        if len(self.prices) < 20:
            return (0.0, 0.0)
        data = list(self.prices)[-20:]
        mean = sum(data) / 20
        std = (sum((x - mean) ** 2 for x in data) / 20) ** 0.5
        return (mean - 2 * std, mean + 2 * std)


class VWAPAccumulator(DequeAccumulatorBase):
    """Volume Weighted Average Price."""
    ACC_FIELDS = ("tuples",)

    def __init__(self, tuples_):
        self.tuples = deque(tuples_)

    @classmethod
    def from_row(cls, row):
        d, h, l, c, v = row
        return cls([(d, h, l, c, v)])

    def compute_result(self):
        pv = 0.0
        v_sum = 0.0
        for _, h, l, c, v in self.tuples:
            pv += ((h + l + c) / 3) * v
            v_sum += v
        return pv / v_sum if v_sum else 0.0


class ATR14Accumulator(DequeAccumulatorBase):
    """Average True Range (14 periods)."""
    ACC_FIELDS = ("records",)

    def __init__(self, records):
        self.records = deque(records)

    @classmethod
    def from_row(cls, row):
        d, h, l, c = row
        return cls([(d, h, l, c)])

    def compute_result(self):
        if len(self.records) < 2:
            return 0.0
        recs = sorted(self.records, key=lambda x: x[0])
        trs = []
        prev_c = None
        for _, h, l, c in recs:
            if prev_c is None:
                tr = h - l
            else:
                tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
            trs.append(tr)
            prev_c = c
        if not trs:
            return 0.0
        return sum(trs[-14:]) / 14 if len(trs) >= 14 else sum(trs) / len(trs)


class OBVAccumulator(DequeAccumulatorBase):
    """On-Balance Volume indicator."""
    ACC_FIELDS = ("history",)

    def __init__(self, history):
        self.history = deque(history)

    @classmethod
    def from_row(cls, row):
        d, c, v = row
        return cls([(d, c, v)])

    def compute_result(self):
        recs = sorted(self.history, key=lambda x: x[0])
        obv = 0.0
        prev_c = None
        for _, c, v in recs:
            if prev_c is not None:
                if c > prev_c:
                    obv += v
                elif c < prev_c:
                    obv -= v
            prev_c = c
        return obv


class CMOAccumulator(DequeAccumulatorBase):
    """Chande Momentum Oscillator."""
    ACC_FIELDS = ("items",)

    def __init__(self, items):
        self.items = deque(items)

    @classmethod
    def from_row(cls, row):
        c, d = row
        return cls([(c, d)])

    def compute_result(self):
        items = sorted(self.items, key=lambda x: x[1])
        prices = [x[0] for x in items]
        if len(prices) < 2:
            return 0.0
        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        relevant = deltas[-14:]
        up = sum(d for d in relevant if d > 0)
        down = sum(-d for d in relevant if d < 0)
        denom = up + down
        return 100 * (up - down) / denom if denom != 0 else 0.0


class CRSIAccumulator(DequeAccumulatorBase):
    """Composite RSI combining RSI, momentum streak, and ROC rank."""
    ACC_FIELDS = ("items",)

    def __init__(self, items):
        self.items = deque(items)

    @classmethod
    def from_row(cls, row):
        c, d = row
        return cls([(c, d)])

    def _rsi_series(self, prices, period):
        """Compute RSI for a given price series and period."""
        if len(prices) < 2:
            return 50.0
        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        if not deltas:
            return 50.0
        avg_g = sum(max(d, 0) for d in deltas[:period]) / period
        avg_l = sum(abs(min(d, 0)) for d in deltas[:period]) / period
        for i in range(period, len(deltas)):
            avg_g = (avg_g * (period - 1) + max(deltas[i], 0)) / period
            avg_l = (avg_l * (period - 1) + abs(min(deltas[i], 0))) / period
        if avg_l == 0:
            return 100.0
        return 100 - 100 / (1 + avg_g / avg_l)

    def compute_result(self):
        items = sorted(self.items, key=lambda x: x[1])
        closes = [x[0] for x in items]
        n = len(closes)
        if n < 3:
            return 50.0
        rsi3 = self._rsi_series(closes, 3)
        streaks = [0] * n
        for i in range(1, n):
            if closes[i] > closes[i - 1]:
                streaks[i] = max(1, streaks[i - 1] + 1)
            elif closes[i] < closes[i - 1]:
                streaks[i] = min(-1, streaks[i - 1] - 1)
        rsi_streak = self._rsi_series(streaks, 2)
        roc = (closes[-1] - closes[-2]) / closes[-2] * 100 if closes[-2] != 0 else 0
        window = [
            (closes[i] - closes[i - 1]) / closes[i - 1] * 100
            for i in range(max(1, n - 100), n)
            if closes[i - 1] != 0
        ]
        rank = (
            sum(1 for x in window if x < roc) / len(window) * 100
            if window
            else 50.0
        )
        return (rsi3 + rsi_streak + rank) / 3


class KlingerAccumulator(DequeAccumulatorBase):
    """Klinger Volume Oscillator."""
    ACC_FIELDS = ("records",)

    def __init__(self, records):
        self.records = deque(records)

    @classmethod
    def from_row(cls, row):
        d, h, l, c, v = row
        return cls([(d, h, l, c, v)])

    def compute_result(self):
        if len(self.records) < 3:
            return (0.0, 0.0, 0.0)
        recs = sorted(self.records, key=lambda x: x[0])
        vf = []
        prev_h = prev_l = prev_c = None
        for _, h, l, c, v in recs:
            if prev_c is not None:
                dm = (h + l + c) - (prev_h + prev_l + prev_c)
                trend = 1 if dm > 0 else -1 if dm < 0 else 1
                vf.append(trend * v)
            prev_h, prev_l, prev_c = h, l, c
        if not vf:
            return (0.0, 0.0, 0.0)

        def ema(vals, span):
            if not vals:
                return []
            k = 2 / (span + 1)
            res = [vals[0]]
            for v in vals[1:]:
                res.append(v * k + res[-1] * (1 - k))
            return res

        e34 = ema(vf, 34)
        e55 = ema(vf, 55)
        min_l = min(len(e34), len(e55))
        ko = [
            e34[i + len(e34) - min_l] - e55[i + len(e55) - min_l]
            for i in range(min_l)
        ]
        sig = ema(ko, 13)
        k = ko[-1]
        s = sig[-1] if sig else 0.0
        return (k, s, k - s)


class KeltnerMidAccumulator(DequeAccumulatorBase):
    """Keltner Channel Midline (EMA-based)."""
    ACC_FIELDS = ("items",)

    def __init__(self, items):
        self.items = deque(items)

    @classmethod
    def from_row(cls, row):
        c, d = row
        return cls([(c, d)])

    def compute_result(self):
        items = sorted(self.items, key=lambda x: x[1])
        closes = [x[0] for x in items]
        if not closes:
            return 0.0
        alpha = 2 / 21
        ema = closes[0]
        for c in closes[1:]:
            ema = c * alpha + ema * (1 - alpha)
        return ema
