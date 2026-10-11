import asyncio
import collections
import math
import ccxt.async_support as ccxt
import config_parametros as cfg

# Estado Global en Memoria para cálculos incrementales (Destruyendo a Pandas)
# Estructura: { "SYMBOL": {"precios": deque, "ema": float} }
estado_memoria = {}

async def obtener_presas(exchange):
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

async def cazar_anomalia(exchange, symbol):
    try:
        # Petición ultra ligera: Solo traemos la ÚLTIMA vela en lugar de 100
        # Esto reduce el payload JSON y acelera la red
        ohlcv = await exchange.fetch_ohlcv(symbol, cfg.TIMEFRAME, limit=1)
        if not ohlcv:
            return None, None
            
        precio_cierre = ohlcv[0][4] # Índice 4 es el precio de cierre ('close')
        
        # Matemáticas Vectorizadas en Microsegundos (O(1))
        z_actual = calcular_z_score_incremental(symbol, precio_cierre)
        
        if z_actual <= cfg.UMBRAL_PANICO:
            print(f"ALERTA: {symbol} | Z-Score: {z_actual:.2f} (POSIBLE COLAPSO)")
            return symbol, z_actual
            
    except Exception as e:
        pass
        
    return None, None

async def main():
    exchange = ccxt.bybit()
    presas = await obtener_presas(exchange)
    print(f"Radar fijado en: {presas}")
    try:
        while True:
            await asyncio.gather(*(cazar_anomalia(exchange, p) for p in presas))
            await asyncio.sleep(10)
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
