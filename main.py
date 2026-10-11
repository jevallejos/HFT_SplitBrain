import asyncio
import ccxt.async_support as ccxt
import importlib

# Importar los tres cerebros (asegúrate de que los nombres de los archivos no tengan caracteres que rompan el import)
radar = importlib.import_module("1_radar_volatilidad")
escudo = importlib.import_module("2_escudo_semantico")
sniper = importlib.import_module("3_ejecutor_sniper")

async def orquestador_principal():
    print("==================================================")
    print("INICIANDO CEREBRO CENTRAL SPLIT-BRAIN HFT")
    print("==================================================")
    
    exchange = ccxt.bybit()
    
    try:
        while True:
            # 1. RADAR: Buscar candidatos con alta volatilidad
            presas = await radar.obtener_presas(exchange)
            print(f"\n[MAIN] Radar escaneando {len(presas)} pares...")
            
            # Cazar anomalías en paralelo
            resultados = await asyncio.gather(*(radar.cazar_anomalia(exchange, p) for p in presas))
            
            # Procesar los resultados del Radar
            for symbol, z_score in resultados:
                if symbol:
                    # Se detectó una caída fuerte (Z-Score crítico)
                    print(f"\n[MAIN] Anomalía confirmada en {symbol}. Activando el Escudo Semántico...")
                    
                    # 2. ESCUDO: Evaluar el riesgo con IA
                    aprobado = await escudo.evaluar_moneda(symbol)
                    
                    if aprobado:
                        # 3. FRANCOTIRADOR: Ejecutar orden de compra
                        print(f"[MAIN] Escudo dio LUZ VERDE. Disparando Francotirador para {symbol}...")
                        exito = await sniper.ejecutar_orden(symbol, z_score)
                        
                        if exito:
                            print(f"[MAIN] ¡Operación exitosa en {symbol}! Esperando desarrollo del mercado.")
                        else:
                            print(f"[MAIN] El Francotirador abortó la misión en {symbol} por problemas de ejecución/saldo.")
                    else:
                        print(f"[MAIN] Operación denegada por el Escudo. Protegiendo capital. Ignorando {symbol}.")
            
            # Esperar antes del siguiente ciclo de escaneo
            await asyncio.sleep(10)
            
    except asyncio.CancelledError:
        print("\n[MAIN] Apagando el bot de forma segura...")
    except Exception as e:
        print(f"\n[MAIN] Error crítico en el orquestador: {e}")
    finally:
        print("\n[MAIN] Cerrando conexión con el exchange...")
        await exchange.close()

if __name__ == "__main__":
    try:
        asyncio.run(orquestador_principal())
    except KeyboardInterrupt:
        print("\n[MAIN] Bot detenido manualmente por el usuario.")
