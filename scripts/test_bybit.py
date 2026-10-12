import asyncio, ccxt.async_support as ccxt

async def main():
    exchange = ccxt.bybit()
    print("Fetching tickers...")
    tickers = await exchange.fetch_tickers()
    print(f"Total tickers fetched: {len(tickers)}")
    if not tickers:
        print("El diccionario de tickers está VACÍO. Bybit en CCXT podría requerir opciones (ej. swap/spot).")
    else:
        # Imprime 3 símbolos cualquiera
        print("Algunos símbolos:", list(tickers.keys())[:3])
        # Busca un símbolo USDT para imprimir su estructura real
        for s, t in tickers.items():
            if 'USDT' in s:
                print(f"\nKeys para {s}:")
                for key, val in t.items():
                    print(f" - {key}: {val} (Tipo: {type(val).__name__})")
                break
    await exchange.close()

if __name__ == "__main__":
    asyncio.run(main())
