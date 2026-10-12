import os
import asyncio
from dotenv import load_dotenv
from groq import AsyncGroq

# Cargar las llaves del búnker
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

async def radar_de_modelos():
    if not API_KEY:
        print("🚨 ERROR: No se encontró GROQ_API_KEY en el .env")
        return

    print("🔌 Escaneando el silicio de los servidores Groq...")
    cliente = AsyncGroq(api_key=API_KEY)
    
    try:
        # Obtener la lista dinámica permitida para TU llave específica
        lista_modelos = await cliente.models.list()
        
        # Filtramos los modelos de voz (whisper)
        modelos_texto = [m.id for m in lista_modelos.data if "whisper" not in m.id.lower()]
        
        print("\n✅ MODELOS ACTIVOS Y PERMITIDOS HOY:")
        print("=" * 50)
        for m in modelos_texto:
            print(f"   -> {m}")
        print("=" * 50)
        print("\n👉 ACCIÓN REQUERIDA:")
        print("Copia exactamente UNO de esos nombres (Prioriza el Llama más moderno, ej: 'llama-3.3-70b-versatile')")

    except Exception as e:
        print(f"\n🚨 Fallo de red o API: {e}")

if __name__ == "__main__":
    asyncio.run(radar_de_modelos())
