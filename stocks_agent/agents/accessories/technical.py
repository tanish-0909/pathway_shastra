"""
Technical Indicators Core Module.

Contains pure calculation logic for technical analysis indicators.
Extracted from technical_agent.py for reusability.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    Core class for calculating technical indicators on OHLCV data.
    
    All methods are designed to work with pandas DataFrames containing
    standard OHLCV columns: open, high, low, close, volume.
    """
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            df: DataFrame with 'close' column
            period: RSI period (default: 14)
            
        Returns:
            pd.Series: RSI values
        """
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.ewm(span=period, adjust=False).mean()
        avg_loss = loss.ewm(span=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calculate_macd(
        df: pd.DataFrame,
        ema_short: int = 12,
        ema_long: int = 26,
        signal_period: int = 9
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate MACD and Signal line.
        
        Args:
            df: DataFrame with 'close' column
            ema_short: Short EMA period (default: 12)
            ema_long: Long EMA period (default: 26)
            signal_period: Signal line period (default: 9)
            
        Returns:
            Tuple of (MACD, Signal) Series
        """
        ema_short_vals = df['close'].ewm(span=ema_short, adjust=False).mean()
        ema_long_vals = df['close'].ewm(span=ema_long, adjust=False).mean()
        macd = ema_short_vals - ema_long_vals
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        return macd, signal
    
    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame,
        period: int = 20,
        std_dev: int = 2
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.
        
        Args:
            df: DataFrame with 'close' column
            period: Moving average period (default: 20)
            std_dev: Standard deviation multiplier (default: 2)
            
        Returns:
            Tuple of (Upper, Middle, Lower) band Series
        """
        middle = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper, middle, lower
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR).
        
        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            period: ATR period (default: 14)
            
        Returns:
            pd.Series: ATR values
        """
        prev_close = df['close'].shift(1)
        tr1 = df['high'] - df['low']
        tr2 = abs(df['high'] - prev_close)
        tr3 = abs(df['low'] - prev_close)
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return true_range.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_vwap(df: pd.DataFrame) -> pd.Series:
        """
        Calculate Volume Weighted Average Price (VWAP).
        
        Args:
            df: DataFrame with 'high', 'low', 'close', 'volume' columns
            
        Returns:
            pd.Series: VWAP values
        """
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        return (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
    
    @staticmethod
    def calculate_stochastic(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Stochastic %K.
        
        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            period: Lookback period (default: 14)
            
        Returns:
            pd.Series: Stochastic %K values
        """
        low_n = df['low'].rolling(window=period).min()
        high_n = df['high'].rolling(window=period).max()
        return 100 * (df['close'] - low_n) / (high_n - low_n)
    
    @staticmethod
    def calculate_mfi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Money Flow Index (MFI).
        
        Args:
            df: DataFrame with 'high', 'low', 'close', 'volume' columns
            period: MFI period (default: 14)
            
        Returns:
            pd.Series: MFI values
        """
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        money_flow = typical_price * df['volume']
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)
        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()
        mfi_ratio = positive_mf / negative_mf
        return 100 - (100 / (1 + mfi_ratio))
    
    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.Series:
        """
        Calculate On-Balance Volume (OBV).
        
        Args:
            df: DataFrame with 'close', 'volume' columns
            
        Returns:
            pd.Series: OBV values
        """
        obv_change = np.where(
            df['close'] > df['close'].shift(1), 
            df['volume'],
            np.where(df['close'] < df['close'].shift(1), -df['volume'], 0)
        )
        obv = np.cumsum(obv_change)
        obv[0] = df.iloc[0]['volume']
        return pd.Series(obv, index=df.index)
    
    @staticmethod
    def calculate_cmo(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Chande Momentum Oscillator (CMO).
        
        Args:
            df: DataFrame with 'close' column
            period: CMO period (default: 14)
            
        Returns:
            pd.Series: CMO values
        """
        price_change = df['close'].diff()
        sum_gains = price_change.where(price_change > 0, 0).rolling(window=period).sum()
        sum_losses = abs(price_change.where(price_change < 0, 0)).rolling(window=period).sum()
        return 100 * ((sum_gains - sum_losses) / (sum_gains + sum_losses))
    
    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Average Directional Index (ADX) with +DI and -DI.
        
        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            period: ADX period (default: 14)
            
        Returns:
            Tuple of (ADX, +DI, -DI) Series
        """
        atr = TechnicalIndicators.calculate_atr(df, period)
        
        plus_dm = df['high'].diff()
        minus_dm = -df['low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        plus_di = 100 * (plus_dm.ewm(span=period, adjust=False).mean() / atr)
        minus_di = 100 * (minus_dm.ewm(span=period, adjust=False).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.ewm(span=period, adjust=False).mean()
        
        return adx, plus_di, minus_di
    
    @classmethod
    def calculate_all_indicators(
        cls,
        df: pd.DataFrame,
        rsi_period: int = 14,
        bb_period: int = 20,
        bb_std: int = 2,
        atr_period: int = 14,
        cmo_period: int = 14,
        ema_short: int = 12,
        ema_long: int = 26,
        macd_signal: int = 9
    ) -> pd.DataFrame:
        """
        Calculate all technical indicators and add them to the DataFrame.
        
        Args:
            df: DataFrame with OHLCV columns
            Various period parameters for indicators
            
        Returns:
            DataFrame with all indicators added
        """
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Sort by date if available
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
        
        # Calculate all indicators
        df['rsi'] = cls.calculate_rsi(df, rsi_period)
        df['vwap'] = cls.calculate_vwap(df)
        
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = cls.calculate_bollinger_bands(
            df, bb_period, bb_std
        )
        
        df['atr'] = cls.calculate_atr(df, atr_period)
        df['cmo'] = cls.calculate_cmo(df, cmo_period)
        
        df['macd'], df['macd_signal'] = cls.calculate_macd(
            df, ema_short, ema_long, macd_signal
        )
        
        # Moving averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        # ROC
        df['roc'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100
        
        # Stochastic
        df['stochastic_k'] = cls.calculate_stochastic(df)
        
        # MFI
        df['mfi'] = cls.calculate_mfi(df)
        
        # ADX
        df['adx'], df['plus_di'], df['minus_di'] = cls.calculate_adx(df)
        
        # Volume ratio
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # OBV
        df['obv'] = cls.calculate_obv(df)
        
        return df
    
    @staticmethod
    def determine_signal(df: pd.DataFrame) -> Tuple[str, str, float, List[Tuple[str, str]]]:
        """
        Determine buy/sell/hold signal based on technical indicators.
        
        Args:
            df: DataFrame with calculated indicators
            
        Returns:
            Tuple of (action, reason, strength, indicator_signals)
        """
        last = df.iloc[-1]
        buy_signals, sell_signals, neutral_signals = [], [], []
        
        # RSI
        if 'rsi' in df.columns and pd.notna(last['rsi']):
            if last['rsi'] < 30:
                buy_signals.append('rsi')
            elif last['rsi'] > 70:
                sell_signals.append('rsi')
            else:
                neutral_signals.append('rsi')
        
        # MACD
        if 'macd' in df.columns and 'macd_signal' in df.columns:
            if last['macd'] > last['macd_signal']:
                buy_signals.append('macd')
            elif last['macd'] < last['macd_signal']:
                sell_signals.append('macd')
            else:
                neutral_signals.append('macd')
        
        # Bollinger Bands
        if 'bb_lower' in df.columns and 'bb_upper' in df.columns:
            if last['close'] <= last['bb_lower']:
                buy_signals.append('bb_low')
            elif last['close'] >= last['bb_upper']:
                sell_signals.append('bb_high')
            else:
                neutral_signals.append('bb')
        
        # SMA Cross
        if 'sma_20' in df.columns and 'sma_50' in df.columns:
            if pd.notna(last['sma_20']) and pd.notna(last['sma_50']):
                if last['sma_20'] > last['sma_50']:
                    buy_signals.append('sma_cross')
                elif last['sma_20'] < last['sma_50']:
                    sell_signals.append('sma_cross')
        
        # Stochastic
        if 'stochastic_k' in df.columns and pd.notna(last['stochastic_k']):
            if last['stochastic_k'] < 20:
                buy_signals.append('stochastic')
            elif last['stochastic_k'] > 80:
                sell_signals.append('stochastic')
        
        # OBV
        if 'obv' in df.columns and len(df) > 1:
            if last['obv'] > df.iloc[-2]['obv']:
                buy_signals.append('obv')
            else:
                sell_signals.append('obv')
        
        # Aggregation
        num_buy = len(buy_signals)
        num_sell = len(sell_signals)
        total = num_buy + num_sell + len(neutral_signals)
        
        if num_buy > 5:
            action = "BUY"
            strength = float(num_buy) if total > 0 else 0.0
            reason = f"BUY: {', '.join(buy_signals)}"
        elif num_sell > 5:
            action = "SELL"
            strength = float(num_sell) if total > 0 else 0.0
            reason = f"SELL: {', '.join(sell_signals)}"
        else:
            action = "HOLD"
            strength = 0.0
            reason = f"HOLD: Mixed signals (Buy: {num_buy}, Sell: {num_sell})"
        
        all_indicators = (
            [(i, "BUY") for i in buy_signals] + 
            [(i, "SELL") for i in sell_signals]
        )
        
        return action, reason, strength, all_indicators

