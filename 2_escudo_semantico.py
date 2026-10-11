import os
from google import genai
import config_parametros as cfg
import asyncio

# Inicializar cliente de Gemini con el nuevo SDK
client = genai.Client(api_key=cfg.GEMINI_API_KEY)

# Usamos el modelo flash
MODELO_GEMINI = 'gemini-3.8-flash'

async def evaluar_moneda(symbol: str) -> bool:
    """
    Actúa como escudo semántico. Interroga a Gemini para saber si el token tiene 
    indicios graves de ser un scam/rug-pull.
    Retorna True si es APROBADO, False si es RECHAZADO.
    """
    token = symbol.split('/')[0] # Extrae "MAGIC" de "MAGIC/USDT:USDT"
    
    prompt = f"""
    Eres el 'Escudo Semantico', un analista de riesgos de criptomonedas de Alta Frecuencia (HFT).
    El radar matemático ha detectado un colapso masivo en el precio del token: {token}.
    
    Tu trabajo es proteger el capital. 
    - Si el token {token} es conocido por ser una estafa, esquema ponzi, 'rug pull' comprobado, o es basura altamente toxica, debes rechazarlo.
    - Si es un proyecto legitimo (como BTC, ETH, SOL, LINK) o una altcoin estándar que simplemente está sufriendo la volatilidad natural del mercado, apruébalo para que el bot compre la caída.
    
    Responde EXCLUSIVAMENTE con una de estas dos palabras (sin signos de puntuacion ni explicaciones extra):
    APROBADO
    RECHAZADO
    """
    
    try:
        # En HFT queremos la respuesta asíncrona para no bloquear el radar
        respuesta = await client.aio.models.generate_content(
            model=MODELO_GEMINI,
            contents=prompt
        )
        texto = respuesta.text.strip().upper()
        
        if "APROBADO" in texto:
            print(f"ESCUDO: {symbol} evaluado -> APROBADO (Vía libre para comprar)")
            return True
        else:
            print(f"ESCUDO: {symbol} evaluado -> RECHAZADO (Peligro detectado)")
            return False
            
    except Exception as e:
        print(f"ESCUDO: Error evaluando {symbol}. Detalle: {e} -> RECHAZADO")
        return False

# Bloque de prueba para verificar que Gemini está conectado y respondiendo
if __name__ == "__main__":
    async def test_escudo():
        print("Iniciando prueba del Escudo Semántico...")
        # Probamos con un activo sólido
        await evaluar_moneda("BTC/USDT:USDT")
        # Probamos con un activo infame por su colapso histórico (Terra LUNA clásico o un token inventado tipo SCAM)
        await evaluar_moneda("SQUID/USDT:USDT") 
    
    asyncio.run(test_escudo())
