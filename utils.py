# utils.py
# Helper functions for WebSocket data fetching, chart generation, and Telegram alerts
import websocket
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import io
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DerivWebSocket:
    def __init__(self, api_token, app_id="1089"):
        self.ws = None
        self.data = {}
        self.connected = False
        self.api_token = api_token
        self.app_id = app_id

    def on_open(self, ws):
        logger.info("WebSocket connected")
        self.connected = True
        self.ws.send(json.dumps({"authorize": self.api_token}))

    def on_message(self, ws, message):
        try:
            msg = json.loads(message)
            if "error" in msg:
                logger.error(f"WebSocket error: {msg['error']['message']}")
                if msg["error"]["code"] == "InvalidToken":
                    logger.error("Invalid API token. Please check .env or config.py.")
                    self.connected = False
                return
            if "authorize" in msg:
                logger.info("Authorization successful")
            if "ticks_history" in msg and "candles" in msg["ticks_history"]:
                symbol = msg["ticks_history"]["symbol"]
                timeframe = msg["ticks_history"]["granularity"]
                self.data[(symbol, timeframe)] = [{
                    "time": datetime.fromtimestamp(c["epoch"]),
                    "open": float(c["open"]),
                    "high": float(c["high"]),
                    "low": float(c["low"]),
                    "close": float(c["close"]),
                    "volume": c.get("volume", 0)
                } for c in msg["ticks_history"]["candles"]]
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")

    def on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")
        self.connected = False

    def on_close(self, ws, close_status_code, close_msg):
        logger.info(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.connected = False

    def connect(self):
        while True:
            try:
                if not self.connected:
                    self.ws = websocket.WebSocketApp(
                        f"wss://ws.binaryws.com/websockets/v3?app_id={self.app_id}",
                        on_open=self.on_open,
                        on_message=self.on_message,
                        on_error=self.on_error,
                        on_close=self.on_close
                    )
                    self.ws.run_forever(ping_interval=30, ping_timeout=10)
                time.sleep(5)
            except Exception as e:
                logger.error(f"WebSocket connection failed: {e}")
                time.sleep(5)  # Retry after 5 seconds

    def fetch_candles(self, symbol, timeframe, count=100):
        try:
            if not self.connected:
                logger.error("WebSocket not connected")
                return None
            granularity = {"M15": 900, "M30": 1800, "H1": 3600, "H4": 14400}.get(timeframe)
            if not granularity:
                logger.error(f"Invalid timeframe: {timeframe}")
                return None
            end_time = int(time.time())
            start_time = end_time - (count * granularity)
            request = {
                "ticks_history": symbol,
                "style": "candles",
                "end": str(end_time),
                "start": str(start_time),
                "count": count,
                "granularity": granularity,
                "adjust_start_time": 1
            }
            self.ws.send(json.dumps(request))
            timeout = time.time() + 5
            while (symbol, timeframe) not in self.data and time.time() < timeout and self.connected:
                time.sleep(0.1)
            return self.data.get((symbol, timeframe))
        except Exception as e:
            logger.error(f"Error fetching candles for {symbol} {timeframe}: {e}")
            return None

def send_telegram_alert(symbol, timeframe, signal, price, holding_time, sl, tp, chart_file, telegram_token, chat_id):
    """
    Send a creative Telegram alert with text and chart image.
    """
    try:
        emoji = "🚀" if signal == "Buy" else "📉"
        message = f"{emoji} *{symbol} {signal} Alert!* | Timeframe: {timeframe} | Hold: ~{holding_time} | Entry: {price:.5f} | SL: {sl:.5f} | TP: {tp:.5f}"
        text_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={chat_id}&text={message}"
        response = requests.get(text_url)
        if response.status_code != 200:
            logger.error(f"Failed to send Telegram text alert: {response.text}")
        photo_url = f"https://api.telegram.org/bot{telegram_token}/sendPhoto?chat_id={chat_id}"
        response = requests.post(photo_url, files={'photo': ('chart.png', chart_file, 'image/png')})
        if response.status_code != 200:
            logger.error(f"Failed to send Telegram chart: {response.text}")
    except Exception as e:
        logger.error(f"Error sending Telegram alert: {e}")

def generate_chart(data, symbol, timeframe, signal, price, sl, tp):
    """
    Generate a candlestick chart with EMAs, SL, TP, and ADX subplot.
    """
    try:
        df = data.copy()
        df["time"] = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True)
        ohlc = df[["open", "high", "low", "close"]].astype(float)
        apds = [
            mpf.make_addplot(df["ema_short"], color="blue", label="8-EMA"),
            mpf.make_addplot(df["ema_long"], color="orange", label="20-EMA"),
            mpf.make_addplot(df["ema_trend"], color="green", label="50-EMA"),
            mpf.make_addplot([price] * len(df), color="purple", linestyle="--", label="Entry"),
            mpf.make_addplot([sl] * len(df), color="red", linestyle="--", label="SL"),
            mpf.make_addplot([tp] * len(df), color="green", linestyle="--", label="TP"),
            mpf.make_addplot(df["adx"], panel=1, color="purple", ylabel="ADX")
        ]
        fig, axes = mpf.plot(
            ohlc.tail(50),
            type="candle",
            addplot=apds,
            title=f"{symbol} {timeframe} {signal}",
            ylabel="Price",
            style="yahoo",
            returnfig=True
        )
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.error(f"Error generating chart for {symbol} {timeframe}: {e}")
        return None
       
