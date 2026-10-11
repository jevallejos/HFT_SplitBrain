import asyncio, ccxt.async_support as ccxt, pandas as pd
import config_parametros as cfg

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

async def cazar_anomalia(exchange, symbol):
    try:
        ohlcv = await exchange.fetch_ohlcv(symbol, cfg.TIMEFRAME, limit=100)
        df = pd.DataFrame(ohlcv, columns=['t','open','high','low','close','v'])
        df['EMA'] = df['close'].ewm(span=cfg.VENTANA, adjust=False).mean()
        df['STD'] = df['close'].rolling(window=cfg.VENTANA).std()
        df['Z-Score'] = (df['close'] - df['EMA']) / df['STD']
        z_actual = df['Z-Score'].iloc[-1]
        if z_actual <= cfg.UMBRAL_PANICO:
            print(f"ALERTA: {symbol} | Z-Score: {z_actual:.2f} (POSIBLE COLAPSO)")
            return symbol, z_actual
    except:
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
