# Functions to calculate EMA, ADX, and ATR indicators using TA-Lib
import pandas as pd
import talib as ta
import logging

logger = logging.getLogger(__name__)

def calculate_indicators(data, ema_short_period, ema_long_period, ema_trend_period, adx_period, atr_period):
    """
    Calculate EMA, ADX, and ATR indicators for given OHLC data.
    
    Args:
        data (list): OHLC data with 'time', 'open', 'high', 'low', 'close', 'volume'.
        ema_short_period (int): Period for short EMA.
        ema_long_period (int): Period for long EMA.
        ema_trend_period (int): Period for trend EMA.
        adx_period (int): Period for ADX.
        atr_period (int): Period for ATR.
    
    Returns:
        pd.DataFrame: DataFrame with EMA, ADX, and ATR columns.
    """
    try:
        df = pd.DataFrame(data)
        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["ema_short"] = ta.EMA(df["close"], timeperiod=ema_short_period)
        df["ema_long"] = ta.EMA(df["close"], timeperiod=ema_long_period)
        df["ema_trend"] = ta.EMA(df["close"], timeperiod=ema_trend_period)
        df["adx"] = ta.ADX(df["high"], df["low"], df["close"], timeperiod=adx_period)
        df["atr"] = ta.ATR(df["high"], df["low"], df["close"], timeperiod=atr_period)
        return df
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
        return None
