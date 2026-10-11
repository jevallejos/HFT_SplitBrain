import asyncio
import time
import ccxt.pro as ccxt
import importlib
import sys

# Redirigir todos los prints a un archivo de log sin perder la consola
class Logger(object):
    def __init__(self, filename="bot_hft.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger()

radar = importlib.import_module("1_radar_volatilidad")
escudo = importlib.import_module("2_escudo_semantico")
sniper = importlib.import_module("3_ejecutor_sniper")
cfg = importlib.import_module("config_parametros")

btc_symbol = "BTC/USDT:USDT"
bloqueo_hasta = 0

async def procesar_anomalia(symbol, z_score):
    """
    Callback asíncrono disparado directamente por el Radar WebSocket
    cuando encuentra una anomalía.
    """
    global bloqueo_hasta
    ahora = time.time()
    
    # 1. GUARDIÁN DE CAOS SISTÉMICO (Si cae el Rey, caen todos)
    if symbol == btc_symbol and z_score <= -4.0:
        print(f"[CIRCUIT BREAKER GLOBAL] ¡BTC COLAPSÓ! Z-Score: {z_score:.2f}")
        print("Bloqueo de compras activado por 30 minutos.")
        bloqueo_hasta = ahora + (30 * 60)
        return
        
    if symbol == btc_symbol:
        return # No procesamos trades en BTC, solo lo usamos de termómetro global
        
    if ahora < bloqueo_hasta:
        restante = int((bloqueo_hasta - ahora) / 60)
        print(f"[BLOQUEO] Anomalía en {symbol} ignorada. Enfriamiento BTC activo: {restante} min.")
        return
        
    # 2. ESCUDO SEMÁNTICO
    print(f"\n[MAIN] Anomalía confirmada en {symbol}. Activando el Escudo Semántico...")
    aprobado = await escudo.evaluar_moneda(symbol)
    
    # 3. FRANCOTIRADOR BIFURCADO
    if aprobado:
        print(f"[MAIN] Escudo dio LUZ VERDE. Disparando Francotirador para {symbol}...")
        exito = await sniper.ejecutar_orden(symbol, z_score)
        if exito:
            print(f"[MAIN] ¡Operación procesada en {symbol}!")
        else:
            print(f"[MAIN] Francotirador abortó misión en {symbol}.")
    else:
        print(f"[MAIN] Operación denegada por el Escudo. Protegiendo capital.")

async def guardian_latencia(exchange):
    """
    Monitorea el desfase temporal con el servidor en un hilo secundario.
    """
    while True:
        try:
            # Usar REST para la latencia base
            server_time = await exchange.fetch_time()
            local_time = int(time.time() * 1000)
            latencia = abs(server_time - local_time)
            if latencia > 2000:
                print(f"[CIRCUIT BREAKER] Latencia INACEPTABLE ({latencia}ms). Riesgo alto en ejecuciones.")
            elif latencia > 300:
                print(f"[WARNING] Latencia alta ({latencia}ms). Flujo WS podría estar retrasado.")
        except Exception:
            pass
        await asyncio.sleep(10)

async def orquestador_principal():
    print("==================================================")
    print("INICIANDO CEREBRO CENTRAL SPLIT-BRAIN HFT (V2.0 - WEBSOCKETS & PAPER TRADING)")
    print("==================================================")
    if cfg.MODO_PAPER:
        print("🟢 MODO PAPER TRADING: ACTIVADO (Las ejecuciones serán simuladas en SQLite)")
    else:
        print("🔴 MODO REAL: ACTIVADO (Dinero real en riesgo)")
    print("==================================================")

    # ccxt.pro para habilitar WebSockets puros
    exchange = ccxt.bybit()
    
    try:
        # Petición inicial para definir top monedas por volumen
        presas = await radar.obtener_presas(exchange)
        if btc_symbol not in presas:
            presas.append(btc_symbol)
            
        print(f"\n[MAIN] Radar WebSockets fijado en {len(presas)} pares: {presas}")
        print("[MAIN] Creando hilos reactivos independientes para cada par...")
        
        # Lanzar el guardián de latencia en background
        asyncio.create_task(guardian_latencia(exchange))
        
        # Lanzar todos los flujos de WebSockets concurrentemente de forma perpetua
        tareas_ws = [radar.cazar_anomalia_ws(exchange, p, procesar_anomalia) for p in presas]
        await asyncio.gather(*tareas_ws)

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
