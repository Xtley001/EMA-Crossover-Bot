# Configuration file for Deriv API, Telegram bot, and strategy parameters
from dotenv import load_dotenv
import os

load_dotenv()

CONFIG = {
    "deriv_api_token": os.getenv("DERIV_API_TOKEN"),
    "telegram_token": os.getenv("TELEGRAM_TOKEN"),
    "chat_id": os.getenv("CHAT_ID"),
    "symbols": [
        "frxEURUSD", "frxUSDJPY", "frxGBPUSD", "frxAUDUSD", "frxUSDCHF", "frxUSDCAD",
        "frxEURJPY", "frxGBPJPY", "frxEURGBP", "frxNZDUSD", "frxEURAUD", "frxGBPAUD",
        "frxEURCAD", "frxAUDJPY", "frxNZDJPY", "frxCADJPY", "frxCHFJPY", "frxGBPCAD",
        "frxAUDNZD", "frxEURNZD", "frxGBPCHF", "frxEURCHF", "frxCADCHF", "frxAUDCAD",
        "frxNZDCAD", "frxGBPNZD", "frxAUDCHF", "frxNZDCHF", "frxEURSGD", "frxUSDSGD",
        "cmdBCOUSD", "cmdUSOIL", "cmdXAUUSD", "cmdXAGUSD", "cmdXPTUSD", "cmdXPDUSD",
        "cmdNGASUSD", "cmdCORNUSD", "idxUS30", "idxSPX500", "idxNAS100", "idxUK100",
        "idxDE40", "idxJP225", "idxAU200", "idxEU50", "idxFR40", "idxHK50",
        "synBTCUSD", "synETHUSD"
    ],
    "timeframes": ["M15", "M30", "H1", "H4"],
    "ema_short": 8,
    "ema_long": 20,
    "ema_trend": 50,
    "adx_period": 14,
    "adx_threshold": 20,
    "atr_period": 14,
    "risk_reward_ratio": 2
}


# To activate a virtual environment (venv), use the following command in your terminal:
# On Windows:
#   .\venv\Scripts\activate
# On macOS/Linux:
#   source venv/bin/activate

