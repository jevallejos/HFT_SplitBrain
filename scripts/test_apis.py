import asyncio, time
import importlib

telemetria = importlib.import_module("4_telemetria_telegram")
escudo = importlib.import_module("2_escudo_semantico")

async def test():
    print("1. Probando Telemetría...")
    await telemetria.enviar_alerta("📡 Prueba de conexión exitosa desde Antigravity IDE.")
    print("   -> Alerta enviada a Telegram.")
    
    print("\n2. Probando Groq LPU...")
    inicio = time.time()
    # Ajusta los parámetros de evaluar_token a lo que pida tu código original
    resultado = await escudo.evaluar_moneda("BTC/USDT:USDT") 
    fin = time.time()
    print(f"   -> Resultado Groq: {resultado}")
    print(f"   -> Tiempo de respuesta: {(fin - inicio)*1000:.2f} ms")

if __name__ == "__main__":
    asyncio.run(test())
