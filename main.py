# Main script to orchestrate the Moving Average Crossover Strategy bot
import time
import logging
from config import CONFIG
from indicators import calculate_indicators
from utils import DerivWebSocket, send_telegram_alert, generate_chart

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_symbol(ws_client, symbol, timeframe):
    """
    Process a symbol and timeframe to detect crossover signals.
    """
    try:
        data = ws_client.fetch_candles(symbol, timeframe)
        if not data:
            return

        df = calculate_indicators(
            data,
            CONFIG["ema_short"],
            CONFIG["ema_long"],
            CONFIG["ema_trend"],
            CONFIG["adx_period"],
            CONFIG["atr_period"]
        )
        if df is None or len(df) < CONFIG["ema_trend"]:
            return

        price = df["close"].iloc[-1]
        ema_short = df["ema_short"].iloc[-1]
        ema_long = df["ema_long"].iloc[-1]
        ema_trend = df["ema_trend"].iloc[-1]
        adx = df["adx"].iloc[-1]
        atr = df["atr"].iloc[-1]

        pip_factor = 0.0001 if "frx" in symbol else 1
        sl_pips = atr / pip_factor
        tp_pips = sl_pips * CONFIG["risk_reward_ratio"]

        holding_times = {"M15": "2 hours", "M30": "4 hours", "H1": "8 hours", "H4": "18 hours"}
        holding_time = holding_times[timeframe]

        if (ema_short > ema_long and 
            df["ema_short"].iloc[-2] <= df["ema_long"].iloc[-2] and 
            price > ema_trend and 
            adx > CONFIG["adx_threshold"]):
            sl = price - atr
            tp = price + (atr * CONFIG["risk_reward_ratio"])
            chart_file = generate_chart(df, symbol, timeframe, "Buy", price, sl, tp)
            if chart_file:
                send_telegram_alert(symbol, timeframe, "Buy", price, holding_time, sl, tp, chart_file,
                                   CONFIG["telegram_token"], CONFIG["chat_id"])
        elif (ema_short < ema_long and 
              df["ema_short"].iloc[-2] >= df["ema_long"].iloc[-2] and 
              price < ema_trend and 
              adx > CONFIG["adx_threshold"]):
            sl = price + atr
            tp = price - (atr * CONFIG["risk_reward_ratio"])
            chart_file = generate_chart(df, symbol, timeframe, "Sell", price, sl, tp)
            if chart_file:
                send_telegram_alert(symbol, timeframe, "Sell", price, holding_time, sl, tp, chart_file,
                                   CONFIG["telegram_token"], CONFIG["chat_id"])
    except Exception as e:
        logger.error(f"Error processing {symbol} {timeframe}: {e}")

def main():
    """
    Main function to run the bot continuously.
    """
    try:
        logger.info("Starting Moving Average Crossover Alert Bot...")
        ws_client = DerivWebSocket(CONFIG["deriv_api_token"])
        ws_client.connect()
        while True:
            for symbol in CONFIG["symbols"]:
                for timeframe in CONFIG["timeframes"]:
                    process_symbol(ws_client, symbol, timeframe)
                    time.sleep(0.5)  # Delay to avoid rate limits
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    finally:
        if ws_client.ws:
            ws_client.ws.close()

if __name__ == "__main__":
    main()
   