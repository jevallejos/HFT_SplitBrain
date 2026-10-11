import ccxt.async_support as ccxt
import config_parametros as cfg
import asyncio

async def ejecutar_orden(symbol: str, z_score: float):
    """
    El Francotirador: Entra en acción solo cuando el Radar detecta un colapso 
    y el Escudo Semántico aprueba el activo.
    """
    print(f"FRANCOTIRADOR: Preparando munición para {symbol} (Z-Score: {z_score:.2f})")
    
    # Nos conectamos con tus llaves API
    exchange = ccxt.bybit({
        'apiKey': cfg.BYBIT_API_KEY,
        'secret': cfg.BYBIT_API_SECRET,
        'enableRateLimit': True,
        'options': {'defaultType': 'linear'} # Bybit USDT Perpetuos
    })
    
    try:
        # Cargar los mercados para poder redondear los decimales de la moneda
        await exchange.load_markets()
        
        # 1. Consultar balance real en tu cuenta
        balance = await exchange.fetch_balance()
        # Extraemos el saldo disponible en USDT
        usdt_disponible = balance.get('USDT', {}).get('free', 0)
        
        if usdt_disponible < 5:
            print("FRANCOTIRADOR: Saldo insuficiente. Abortando misión.")
            return False
            
        # 2. Gestión de Riesgo Extrema (Criterio de Kelly)
        inversion = usdt_disponible * cfg.KELLY_MAX_PCT
        print(f"FRANCOTIRADOR: Saldo: {usdt_disponible:.2f} USDT | Invirtiendo: {inversion:.2f} USDT (Kelly {cfg.KELLY_MAX_PCT*100}%)")
        
        # 3. Calcular cantidad de moneda a comprar
        ticker = await exchange.fetch_ticker(symbol)
        precio_actual = ticker['last']
        cantidad_cruda = inversion / precio_actual
        # Ajustamos los decimales a lo que acepta Bybit
        cantidad = float(exchange.amount_to_precision(symbol, cantidad_cruda))
        
        # 4. Establecemos escudo de protección (Stop-Loss -3%) y Take-Profit (+5%)
        stop_loss_price = precio_actual * 0.97
        take_profit_price = precio_actual * 1.05
        
        print(f"FRANCOTIRADOR: Disparando orden Market BUY -> {cantidad} {symbol} a {precio_actual}")
        print(f"FRANCOTIRADOR: [SIMULACIÓN] Stop-Loss: {stop_loss_price:.4f} | Take-Profit: {take_profit_price:.4f}")
        
        # =========================================================
        # SEGURO PUESTO: Las líneas de abajo están comentadas para 
        # que el bot no compre con dinero real mientras probamos.
        # =========================================================
        """
        orden = await exchange.create_order(
            symbol=symbol,
            type='market',
            side='buy',
            amount=cantidad,
            params={
                'stopLoss': stop_loss_price,
                'takeProfit': take_profit_price
            }
        )
        print(f"FRANCOTIRADOR: ¡Blanco abatido! Orden ejecutada. ID: {orden['id']}")
        """
        return True

    except Exception as e:
        print(f"FRANCOTIRADOR: Arma encasquillada (Error): {e}")
        return False
    finally:
        await exchange.close()

if __name__ == "__main__":
    # Prueba de "Gatillo Seco"
    asyncio.run(ejecutar_orden("MAGIC/USDT:USDT", -4.2))
