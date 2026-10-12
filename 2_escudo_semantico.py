import os
from groq import AsyncGroq
import config_parametros as cfg
import asyncio

# Inicializar cliente asíncrono de Groq
cliente_groq = AsyncGroq(api_key=cfg.GROQ_API_KEY)

MODELO_GROQ = 'openai/gpt-oss-20b'

async def evaluar_moneda(symbol: str) -> bool:
    """
    Actúa como escudo semántico. Interroga a Groq (Llama 3) para saber si el token tiene 
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
    
    Responde EXCLUSIVAMENTE con un JSON válido usando el siguiente formato:
    {{"decision": "APROBADO"}} o {{"decision": "RECHAZADO"}}
    """
    
    try:
        respuesta = await cliente_groq.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODELO_GROQ,
            response_format={"type": "json_object"},
            temperature=0.0
        )
        texto = respuesta.choices[0].message.content.strip().upper()
        
        if "APROBADO" in texto:
            print(f"ESCUDO (Groq): {symbol} evaluado -> APROBADO (Vía libre para comprar)")
            return True
        else:
            print(f"ESCUDO (Groq): {symbol} evaluado -> RECHAZADO (Peligro detectado)")
            return False
            
    except Exception as e:
        print(f"ESCUDO (Groq): Error evaluando {symbol}. Detalle: {e} -> RECHAZADO")
        return False

if __name__ == "__main__":
    async def test_escudo():
        print("Iniciando prueba del Escudo Semántico con Groq...")
        await evaluar_moneda("BTC/USDT:USDT")
        await evaluar_moneda("SQUID/USDT:USDT") 
    
    asyncio.run(test_escudo())
