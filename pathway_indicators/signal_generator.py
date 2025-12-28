"""
Signal Generation and UDF Extractors
Trading signal logic and some utility functions for indicator extraction.
"""

import pathway as pw
from typing import Dict, Any, Optional, Tuple
import joblib
import numpy as np
import os
from sklearn.ensemble import HistGradientBoostingRegressor


MODEL_PATH = "sklearn_trading_model.pkl"
ML_WEIGHT = 3
ML_THRESHOLD = 0.0000

ml_model = None
if os.path.exists(MODEL_PATH):
    try:
        ml_model = joblib.load(MODEL_PATH)
    except Exception:
        pass


@pw.udf(deterministic=True)
def enhanced_signal_generator(
    close, macd_tuple, rsi, atr, min_low, max_high,
    sma_20, sma_50, volume, vwap, bb_tuple,
    crsi, klinger_tuple, keltner, cmo, 
    sell_threshold=5, buy_threshold=5
) -> Dict[str, Any]:
    """
    Generate trading signals based on multiple technical indicators.
    
    Args:
        close: Closing prices tuple
        macd_tuple: (macd, signal, histogram)
        rsi: RSI value
        atr: Average True Range
        min_low: Minimum low price in window
        max_high: Maximum high price in window
        sma_20: 20-period SMA
        sma_50: 50-period SMA
        volume: Volume tuple
        vwap: Volume Weighted Average Price
        bb_tuple: Bollinger Bands (low, high)
        crsi: Composite RSI
        klinger_tuple: Klinger oscillator (klinger, signal, histogram)
        keltner: Keltner channel (mid, upper, lower)
        cmo: Chande Momentum Oscillator
        sell_threshold: Minimum conditions for SELL signal
        buy_threshold: Minimum conditions for BUY signal
        
    Returns:
        Dictionary with action, stop_loss, take_profit, and indicator values
    """
    macd, macd_sig, macd_hist = macd_tuple
    bb_low = bb_tuple[0]
    bb_high = bb_tuple[1]
    
    klinger, klinger_sig, klinger_hist = klinger_tuple
    kelt_mid, kelt_up, kelt_low = keltner

    current_price = close[1]
    current_volume = volume[1]

    # Risk Management Constants
    SL_ATR_MULT = 1.0
    TP_ATR_MULT = 1.5
    LIMIT_ORDER_AT_MULT = 0.25

    action = "HOLD"
    stop_loss = 0.0
    take_profit = 0.0
    signal_strength = 0
    limit_order = 0.0
    reason = ""

    if atr is None:
        atr = 0.0
    if cmo is None:
        cmo = 0.0

    # Guard against invalid data
    if current_price < min_low or current_volume == 0:
        return {
            "action": action, "stop_loss": stop_loss, "take_profit": take_profit,
            "signal_strength": signal_strength, "current_price": current_price,
            "rsi": rsi, "macd": macd, "macd_signal": macd_sig, "macd_hist": macd_hist,
            "sma20": sma_20, "sma50": sma_50, "volume": volume, "vwap": vwap,
            "bb_low": bb_low, "bb_high": bb_high, "limit_order": limit_order,
            "crsi": crsi, "klinger": klinger, "klinger_signal": klinger_sig,
            "klinger_hist": klinger_hist, "keltner_mid": kelt_mid, 
            "keltner_up": kelt_up, "keltner_low": kelt_low, "cmo": cmo,
            "reasons": reason,
        }

    # BUY Logic
    buy_conditions = 0
    
    # 1. MACD: Positive cross (MACD > Signal)
    if macd > macd_sig and macd_hist > 0:
        buy_conditions += 1
        reason += "macd says BUY, "
    
    # 2. RSI: Oversold recovery zone
    if 25 < rsi < 45:
        buy_conditions += 1
        reason += "rsi says BUY, "
    
    # 3. CRSI: Composite RSI oversold
    if crsi is not None and crsi < 25:
        buy_conditions += 1
        reason += "crsi says BUY, "
    
    # 4. Bollinger Bands: Touch lower band
    if bb_low and current_price <= bb_low:
        buy_conditions += 1
        reason += "bb_low says BUY, "
    
    # 5. VWAP: Price at or above VWAP
    if vwap and current_price >= vwap*1.01:
        buy_conditions += 1
        reason += "vwap says BUY, "
    
    # 6. Keltner: Touch lower band
    if kelt_low and current_price <= kelt_low:
        buy_conditions += 1
        reason += "keltner_low says BUY, "
    
    # 7. Klinger: Positive cross (Klinger > Signal)
    if klinger > klinger_sig and klinger_hist > 0:
        buy_conditions += 1
        reason += "klinger says BUY, "
    
    # 8. SMA: Golden Cross (SMA20 > SMA50)
    if sma_20 is not None and sma_50 is not None and sma_20 > sma_50:
        buy_conditions += 1
        reason += "sma_trend says BUY, "
    
    # 9. CMO: Oversold condition
    if cmo < -30:
        buy_conditions += 1
        reason += "cmo says BUY, "

    # SELL Logic
    sell_conditions = 0
    
    # 1. MACD: Negative cross (MACD < Signal)
    if macd < macd_sig and macd_hist < 0:
        sell_conditions += 1
        reason += "macd says SELL, "
    
    # 2. RSI: Overbought zone
    if 55 < rsi < 75:
        sell_conditions += 1
        reason += "rsi says SELL, "
    
    # 3. CRSI: Composite RSI overbought
    if crsi is not None and crsi > 75:
        sell_conditions += 1
        reason += "crsi says SELL, "
    
    # 4. Recent High: Price drop from peak
    if current_price < max_high * 0.99:
        sell_conditions += 1
    
    # 5. Bollinger Bands: Touch upper band
    if bb_high and current_price >= bb_high:
        sell_conditions += 1
        reason += "bb_high says SELL, "
    
    # 6. VWAP: Price below VWAP
    if vwap and current_price <= 0.99*vwap:
        sell_conditions += 1
        reason += "vwap says SELL, "
    
    # 7. Keltner: Touch upper band
    if kelt_up and current_price >= kelt_up:
        sell_conditions += 1
        reason += "kelt_up says SELL, "
    
    # 8. Klinger: Negative cross (Klinger < Signal)
    if klinger < klinger_sig and klinger_hist < 0:
        sell_conditions += 1
        reason += "klinger says SELL, "
    
    # 9. SMA: Death Cross (SMA20 < SMA50)
    if sma_20 is not None and sma_50 is not None and sma_20 < sma_50:
        sell_conditions += 1
        reason += "sma says SELL, "
    
    # 11. CMO: Overbought condition
    if cmo > 30:
        sell_conditions += 1
        reason += "cmo says SELL, "

    if ml_model is not None:
        try:
            f_rsi = rsi if rsi is not None else 50.0
            f_cmo = cmo
            f_crsi = crsi if crsi is not None else 50.0
            
            f_macd_rel = (macd / current_price * 100) if current_price else 0.0
            f_atr_pct = (atr / current_price * 100) if current_price else 0.0
            f_sma20_dist = ((current_price - sma_20) / sma_20 * 100) if sma_20 else 0.0
            f_sma50_dist = ((current_price - sma_50) / sma_50 * 100) if sma_50 else 0.0
            f_vwap_dist = ((current_price - vwap) / vwap * 100) if vwap else 0.0
            
            bb_range = bb_high - bb_low
            f_bb_pos = ((current_price - bb_low) / bb_range) if bb_range != 0 else 0.5
            
            kelt_range = kelt_up - kelt_low
            f_kelt_pos = ((current_price - kelt_low) / kelt_range) if kelt_range != 0 else 0.5
            
            vol_avg = sum(volume) / len(volume) if volume and len(volume) > 0 else 1.0
            f_vol_rel = (current_volume / vol_avg) if vol_avg != 0 else 1.0

            features = np.array([[
                f_rsi, f_cmo, f_crsi, f_macd_rel, f_atr_pct, 
                f_sma20_dist, f_sma50_dist, f_vwap_dist, 
                f_bb_pos, f_kelt_pos, f_vol_rel
            ]])
            
            ml_pred = ml_model.predict(features)[0]

            if ml_pred > ML_THRESHOLD:
                buy_conditions += ML_WEIGHT
                reason += f"xgb says buy with confidence ({ml_pred:.4f}), "
            elif ml_pred < -ML_THRESHOLD:
                sell_conditions += ML_WEIGHT
                reason += f"xgb says sell with confidence ({ml_pred:.4f}), "
            sell_threshold += 2.0
            buy_threshold += 2.0
        except Exception:
            pass

    if buy_conditions >= buy_threshold:
        action = "BUY"
        stop_loss = current_price - (SL_ATR_MULT * atr)
        take_profit = current_price + (TP_ATR_MULT * atr)
        signal_strength = buy_conditions
        limit_order = current_price - (LIMIT_ORDER_AT_MULT * atr)

    if sell_conditions >= sell_threshold and action != "BUY":
        action = "SELL"
        stop_loss = 0.0
        take_profit = 0.0
        signal_strength = sell_conditions
        limit_order = current_price - (LIMIT_ORDER_AT_MULT * atr)

    return {
        "action": action, "stop_loss": stop_loss, "take_profit": take_profit,
        "signal_strength": signal_strength, "current_price": current_price,
        "rsi": rsi, "macd": macd, "macd_signal": macd_sig, "macd_hist": macd_hist,
        "sma20": sma_20, "sma50": sma_50, "volume": volume, "vwap": vwap,
        "bb_low": bb_low, "bb_high": bb_high, "limit_order": limit_order,
        "crsi": crsi, "klinger": klinger, "klinger_signal": klinger_sig,
        "klinger_hist": klinger_hist, "keltner_mid": kelt_mid, 
        "keltner_up": kelt_up, "keltner_low": kelt_low, "cmo": cmo,
        "reasons": reason,
    }


# UDF Extractors - Signal Dictionary Accessors
@pw.udf(deterministic=True)
def get_action(s: Dict[str, Any]) -> str:
    """Extract action field from signal dictionary."""
    try:
        return str(s["action"]).replace('"', '')
    except:
        return "HOLD"


@pw.udf(deterministic=True)
def get_stop_loss(s: Dict[str, Any]) -> float:
    """Extract stop_loss field from signal dictionary."""
    try:
        return float(s["stop_loss"])
    except:
        return 0.0


@pw.udf(deterministic=True)
def get_take_profit(s: Dict[str, Any]) -> float:
    """Extract take_profit field from signal dictionary."""
    try:
        return float(s["take_profit"])
    except:
        return 0.0


@pw.udf(deterministic=True)
def get_signal_strength(s: Dict[str, Any]) -> float:
    """Extract signal_strength field from signal dictionary."""
    try:
        return float(s["signal_strength"])
    except:
        return 0.0


@pw.udf(deterministic=True)
def get_current_price(s: Dict[str, Any]) -> float:
    """Extract current_price field from signal dictionary."""
    try:
        return float(s["current_price"])
    except:
        return 0.0


@pw.udf(deterministic=True)
def get_rsi(s: Dict[str, Any]) -> float:
    """Extract RSI field from signal dictionary."""
    try:
        return float(s["rsi"])
    except:
        return 0.0


@pw.udf(deterministic=True)
def get_macd(s: Dict[str, Any]) -> float:
    """Extract MACD field from signal dictionary."""
    try:
        return float(s["macd"])
    except:
        return 0.0


@pw.udf(deterministic=True)
def get_macd_signal(s: Dict[str, Any]) -> float:
    """Extract MACD signal field from signal dictionary."""
    try:
        return float(s["macd_signal"])
    except:
        return 0.0


@pw.udf(deterministic=True)
def get_macd_hist(s: Dict[str, Any]) -> float:
    """Extract MACD histogram field from signal dictionary."""
    try:
        return float(s["macd_hist"])
    except:
        return 0.0


@pw.udf(deterministic=True)
def get_limit_order(s: Dict[str, Any]) -> float:
    """Extract limit_order field from signal dictionary."""
    try:
        return float(s["limit_order"])
    except:
        return 0.0


@pw.udf(deterministic=True)
def get_sma(s: Dict[str, Any]) -> list:
    """Extract SMA values (20, 50) from signal dictionary."""
    try:
        return [float(s["sma20"]), float(s["sma50"])]
    except:
        return [0.0, 0.0]


@pw.udf(deterministic=True)
def get_vwap(s: Dict[str, Any]) -> float:
    """Extract VWAP field from signal dictionary."""
    try:
        return float(s["vwap"])
    except:
        return 0.0


@pw.udf(deterministic=True)
def get_bb(s: Dict[str, Any]) -> list:
    """Extract Bollinger Bands (low, high) from signal dictionary."""
    try:
        return [float(s["bb_low"]), float(s["bb_high"])]
    except:
        return [0.0, 0.0]


@pw.udf(deterministic=True)
def get_crsi(s: Dict[str, Any]) -> float:
    """Extract Composite RSI field from signal dictionary."""
    try:
        return float(s["crsi"])
    except:
        return 0.0


@pw.udf(deterministic=True)
def get_klinger(s: Dict[str, Any]) -> list:
    """Extract Klinger values (klinger, signal, histogram) from signal dictionary."""
    try:
        return [float(s["klinger"]), float(s["klinger_signal"]), float(s["klinger_hist"])]
    except:
        return [0.0, 0.0, 0.0]


@pw.udf(deterministic=True)
def get_keltner(s: Dict[str, Any]) -> list:
    """Extract Keltner values (mid, up, low) from signal dictionary."""
    try:
        return [float(s["keltner_mid"]), float(s["keltner_up"]), float(s["keltner_low"])]
    except:
        return [0.0, 0.0, 0.0]


@pw.udf(deterministic=True)
def get_cmo(s: Dict[str, Any]) -> float:
    """Extract CMO field from signal dictionary."""
    try:
        return float(s["cmo"])
    except (KeyError, TypeError, ValueError):
        return 0.0


@pw.udf(deterministic=True)
def get_reason(s: Dict[str, Any]) -> str:
    """Extract reason field from signal dictionary."""
    try:
        return str(s["reasons"])
    except (KeyError, TypeError, ValueError):
        return ""


@pw.udf
def is_not_hold(action: str) -> bool:
    """Check if action is not HOLD."""
    try:
        return str(action).strip().replace('"', '').upper() != "HOLD"
    except Exception:
        return False


# Helper UDF for Keltner Channel

@pw.udf(deterministic=True)
def build_keltner_tuple(mid: float, atr: float, mult: float = 2.0) -> Tuple[float, float, float]:
    """
    Build Keltner channel tuple from midline and ATR.
    
    Args:
        mid: Midline (EMA) value
        atr: Average True Range
        mult: Multiplier for ATR bands (default: 2.0)
        
    Returns:
        Tuple of (midline, upper_band, lower_band)
    """
    if mid is None or atr is None:
        return (None, None, None)
    return (mid, mid + mult * atr, mid - mult * atr)
