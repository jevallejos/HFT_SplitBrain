import asyncio
import time
import ccxt.async_support as ccxt
import importlib

# Importar los tres cerebros (asegúrate de que los nombres de los archivos no tengan caracteres que rompan el import)
radar = importlib.import_module("1_radar_volatilidad")
escudo = importlib.import_module("2_escudo_semantico")
sniper = importlib.import_module("3_ejecutor_sniper")

async def orquestador_principal():
    print("==================================================")
    print("INICIANDO CEREBRO CENTRAL SPLIT-BRAIN HFT (OPTIMIZADO V1.1)")
    print("==================================================")
    
    exchange = ccxt.bybit()
    bloqueo_hasta = 0  # Timestamp para el Circuit Breaker de BTC
    
    # 1. SOLUCIÓN CORTO PLAZO: Estrangulamiento Asíncrono para evitar Baneos (429)
    semaforo_api = asyncio.Semaphore(10)
    
    async def escaneo_seguro(simbolo):
        async with semaforo_api:
            return await radar.cazar_anomalia(exchange, simbolo)

    try:
        while True:
            ahora = time.time()
            
            # 2. GUARDIÁN DE DESFASE TEMPORAL (Time Drift)
            try:
                server_time = await exchange.fetch_time()
                local_time = int(time.time() * 1000)
                latencia = abs(server_time - local_time)
                if latencia > 300:
                    print(f"⚠️ [CIRCUIT BREAKER] Latencia de red extrema ({latencia}ms). Pausando motor...")
                    await asyncio.sleep(5)
                    continue
            except Exception as e:
                print(f"⚠️ Error obteniendo hora del servidor: {e}")
                await asyncio.sleep(5)
                continue

            # 3. GUARDIÁN DE CAOS SISTÉMICO (Enfriamiento por caída de BTC)
            if ahora < bloqueo_hasta:
                restante = int((bloqueo_hasta - ahora) / 60)
                print(f"🛑 [SISTEMA BLOQUEADO] Cisne Negro detectado. Enfriamiento activo: {restante} min restantes.")
                await asyncio.sleep(60) # Chequeamos cada minuto si ya pasó el castigo
                continue

            # RADAR: Buscar candidatos
            presas = await radar.obtener_presas(exchange)
            
            # Obligamos a monitorear BTC siempre para nuestro Guardián Sistémico
            btc_symbol = "BTC/USDT:USDT"
            if btc_symbol not in presas:
                presas.append(btc_symbol)

            print(f"\n[MAIN] Radar escaneando {len(presas)} pares (Torniquete: 10 a la vez)...")
            
            # Ejecución concurrente estrangulada (Máximo 10 peticiones a la vez)
            resultados = await asyncio.gather(*(escaneo_seguro(p) for p in presas))
            
            # Procesar los resultados del Radar
            for symbol, z_score in resultados:
                if symbol:
                    # Validar Caos Sistémico (Si cae el Rey, caen todos)
                    if symbol == btc_symbol and z_score <= -4.0:
                        print(f"🚨🚨 [CIRCUIT BREAKER GLOBAL] ¡BTC COLAPSÓ! Z-Score: {z_score:.2f}")
                        print("🚨🚨 Bloqueo de compras activado por 30 minutos.")
                        bloqueo_hasta = time.time() + (30 * 60)
                        break # Ignoramos cualquier otra altcoin en esta ronda
                    
                    if symbol == btc_symbol:
                        continue # No disparamos a BTC, solo lo usamos de termómetro global
                        
                    # Se detectó una caída fuerte en Altcoin (y no hay Caos Sistémico)
                    print(f"\n[MAIN] Anomalía confirmada en {symbol}. Activando el Escudo Semántico...")
                    aprobado = await escudo.evaluar_moneda(symbol)
                    
                    if aprobado:
                        print(f"[MAIN] Escudo dio LUZ VERDE. Disparando Francotirador para {symbol}...")
                        exito = await sniper.ejecutar_orden(symbol, z_score)
                        
                        if exito:
                            print(f"[MAIN] ¡Operación exitosa en {symbol}! Esperando desarrollo del mercado.")
                        else:
                            print(f"[MAIN] El Francotirador abortó la misión en {symbol} por problemas de ejecución/saldo.")
                    else:
                        print(f"[MAIN] Operación denegada por el Escudo. Protegiendo capital. Ignorando {symbol}.")
            
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
