import os
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")

KELLY_MAX_PCT = 0.05
TIMEFRAME = '1m'
VENTANA = 60
UMBRAL_PANICO = -3.5
VOL_MIN_USDT = 50_000_000
TOP_N = 5
PROHIBIDAS = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'USDC/USDT:USDT', 'USDE/USDT:USDT']

# Parámetros Paper Trading & Riesgo
MODO_PAPER = True
SL_PCT = 0.03
TP_PCT = 0.05
