import asyncio
import collections
import math
import ccxt.pro as ccxt
import config_parametros as cfg
import importlib

# Estado Global en Memoria para cálculos incrementales (Destruyendo a Pandas)
# Estructura: { "SYMBOL": {"precios": deque, "ema": float} }
estado_memoria = {}

async def obtener_presas(exchange):
    # Usamos REST inicialmente solo para buscar volumen
    tickers = await exchange.fetch_tickers()
    presas = []
    for s, t in tickers.items():
        if s.endswith('/USDT:USDT') and s not in cfg.PROHIBIDAS:
            vol = t.get('quoteVolume')
            if vol and vol > cfg.VOL_MIN_USDT:
                pct = t.get('percentage')
                presas.append((s, abs(pct) if pct else 0))
    presas.sort(key=lambda x: x[1], reverse=True)
    return [p[0] for p in presas[:cfg.TOP_N]]

def calcular_z_score_incremental(symbol, precio_actual):
    if symbol not in estado_memoria:
        # Inicialización de la caché para este par
        estado_memoria[symbol] = {
            "precios": collections.deque(maxlen=cfg.VENTANA),
            "ema": precio_actual
        }
    
    estado = estado_memoria[symbol]
    estado["precios"].append(precio_actual)
    
    # Cálculo Incremental de la EMA: EMA_hoy = Precio_hoy * K + EMA_ayer * (1 - K)
    k = 2 / (cfg.VENTANA + 1)
    estado["ema"] = (precio_actual * k) + (estado["ema"] * (1 - k))
    
    # Si no tenemos suficientes datos para la Desviación Estándar, no disparamos alertas falsas
    n = len(estado["precios"])
    if n < 2:
        return 0.0

    # Cálculo ultra-rápido de la Desviación Estándar de la muestra
    media = sum(estado["precios"]) / n
    varianza = sum((x - media) ** 2 for x in estado["precios"]) / (n - 1)
    std = math.sqrt(varianza)
    
    if std == 0:
        return 0.0
        
    z_score = (precio_actual - estado["ema"]) / std
    return z_score

async def cazar_anomalia_ws(exchange, symbol, callback=None):
    """
    Bucle reactivo con WebSockets (ccxt.pro).
    Reemplaza la lógica REST y el Semaphore.
    """
    simulador = None
    if cfg.MODO_PAPER:
        simulador = importlib.import_module("0_simulador_pnl")

    while True:
        try:
            # Bucle Reactivo: Espera activa sin REST
            ticker = await exchange.watch_ticker(symbol)
            last = ticker.get('last')
            
            if not last:
                continue
            
            # 1. Enviar el precio al simulador si MODO_PAPER es True
            if cfg.MODO_PAPER and simulador:
                simulador.vigilar_posiciones_virtuales(symbol, last)
                
            # 2. Inyectar precio en la memoria O(1)
            z_actual = calcular_z_score_incremental(symbol, last)
            
            # 3. Disparador
            if z_actual <= cfg.UMBRAL_PANICO:
                print(f"[WS] ALERTA: {symbol} | Z-Score: {z_actual:.2f} (POSIBLE COLAPSO)")
                if callback:
                    await callback(symbol, z_actual)
                # Pausa temporal tras detectar caída para evitar flood de señales
                await asyncio.sleep(60)
                
        except Exception as e:
            # ccxt.pro maneja la reconexión, pero evitamos crashear el loop en errores inesperados
            await asyncio.sleep(5)
