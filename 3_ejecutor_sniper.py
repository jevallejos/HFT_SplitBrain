import ccxt.async_support as ccxt
import config_parametros as cfg
import asyncio
import importlib

async def ejecutar_orden(symbol: str, z_score: float):
    """
    El Francotirador Bifurcado:
    Si MODO_PAPER es True, envía la orden al simulador en RAM.
    Si es False, dispara dinero real en Bybit.
    """
    print(f"FRANCOTIRADOR: Preparando munición para {symbol} (Z-Score: {z_score:.2f})")
    
    exchange = ccxt.bybit({
        'apiKey': cfg.BYBIT_API_KEY,
        'secret': cfg.BYBIT_API_SECRET,
        'enableRateLimit': True,
        'options': {'defaultType': 'linear'} # Bybit USDT Perpetuos
    })
    
    try:
        await exchange.load_markets()
        
        # 1. Consultar balance real
        balance = await exchange.fetch_balance()
        usdt_disponible = balance.get('USDT', {}).get('free', 0)
        
        # Fondeo virtual automático si estamos en Paper Trading y la cuenta real está vacía
        if cfg.MODO_PAPER and usdt_disponible < 5:
            usdt_disponible = 1000.0
            
        if usdt_disponible < 5:
            print("FRANCOTIRADOR: Saldo insuficiente. Abortando misión.")
            return False
            
        # 2. Gestión de Riesgo (Kelly)
        inversion = usdt_disponible * cfg.KELLY_MAX_PCT
        print(f"FRANCOTIRADOR: Saldo Base: {usdt_disponible:.2f} USDT | Invirtiendo: {inversion:.2f} USDT")
        
        # 3. Calcular cantidad a comprar
        ticker = await exchange.fetch_ticker(symbol)
        precio_actual = ticker['last']
        cantidad_cruda = inversion / precio_actual
        cantidad = float(exchange.amount_to_precision(symbol, cantidad_cruda))
        
        stop_loss_price = precio_actual * (1 - cfg.SL_PCT)
        take_profit_price = precio_actual * (1 + cfg.TP_PCT)
        
        # =========================================================
        # BIFURCACIÓN DE EJECUCIÓN (PAPER VS REAL)
        # =========================================================
        if cfg.MODO_PAPER:
            simulador = importlib.import_module("0_simulador_pnl")
            print(f"🟩 [ALERTA VERDE - PAPER TRADING] Interceptando orden de compra Market para {symbol}")
            simulador.abrir_posicion_virtual(symbol, precio_actual, 'buy')
            return True
        else:
            print(f"FRANCOTIRADOR [REAL]: Disparando orden LIMIT (PostOnly) BUY -> {cantidad} {symbol} a {precio_actual}")
            print(f"FRANCOTIRADOR [REAL]: Stop-Loss: {stop_loss_price:.4f} | Take-Profit: {take_profit_price:.4f}")
            
            telemetria = importlib.import_module("4_telemetria_telegram")
            enviar_alerta = telemetria.enviar_alerta
            
            try:
                orden = await exchange.create_order(
                    symbol=symbol,
                    type='limit',
                    side='buy',
                    amount=cantidad,
                    price=precio_actual,
                    params={
                        'timeInForce': 'PostOnly',
                        'stopLoss': stop_loss_price,
                        'takeProfit': take_profit_price
                    }
                )
                print(f"FRANCOTIRADOR [REAL]: ¡Blanco abatido! Orden ejecutada. ID: {orden['id']}")
                asyncio.create_task(enviar_alerta(f"🟩 ALERTA VERDE (PROD):\nOrden Limit PostOnly creada en {symbol}\nPrecio: {precio_actual}\nID: {orden['id']}"))
                return True
            except Exception as e:
                print(f"FRANCOTIRADOR [ERROR REAL]: {e}")
                asyncio.create_task(enviar_alerta(f"🚨 ERROR EJECUTANDO ORDEN REAL en {symbol}:\n{e}"))
                return False

    except Exception as e:
        print(f"FRANCOTIRADOR: Arma encasquillada (Error): {e}")
        return False
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(ejecutar_orden("MAGIC/USDT:USDT", -4.2))
