import aiohttp
import config_parametros as cfg

async def enviar_alerta(mensaje: str):
    if not cfg.TELEGRAM_TOKEN or not cfg.TELEGRAM_CHAT_ID: return
    url = f"https://api.telegram.org/bot{cfg.TELEGRAM_TOKEN}/sendMessage"
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={"chat_id": cfg.TELEGRAM_CHAT_ID, "text": mensaje}, timeout=5)
    except Exception:
        pass
