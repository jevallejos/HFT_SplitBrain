import sqlite3
import time
import config_parametros as cfg

DB_NAME = 'paper_trading.db'

# Diccionario global en RAM para máxima velocidad O(1)
posiciones_activas = {}

def inicializar_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial_paper (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            side TEXT,
            entry REAL,
            exit REAL,
            pnl REAL,
            time INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Ejecutar al importar el módulo para asegurar que la tabla exista
inicializar_db()

def abrir_posicion_virtual(symbol: str, price: float, side: str = 'buy'):
    """Abre una posición simulada con slippage del 0.15%."""
    slippage = 0.0015
    
    if side == 'buy':
        precio_ejecucion = price * (1 + slippage)
        sl_price = precio_ejecucion * (1 - cfg.SL_PCT)
        tp_price = precio_ejecucion * (1 + cfg.TP_PCT)
    else: # short
        precio_ejecucion = price * (1 - slippage)
        sl_price = precio_ejecucion * (1 + cfg.SL_PCT)
        tp_price = precio_ejecucion * (1 - cfg.TP_PCT)
        
    posiciones_activas[symbol] = {
        'entry': precio_ejecucion,
        'side': side,
        'sl': sl_price,
        'tp': tp_price,
        'time': int(time.time() * 1000)
    }
    msg = f"[PAPER] 🟢 Posición ABIERTA: {symbol} | Side: {side} | Entry: {precio_ejecucion:.4f}"
    print(msg)
    
    # Importar aquí para evitar referencias circulares si las hay
    import importlib
    import asyncio
    telemetria = importlib.import_module("4_telemetria_telegram")
    asyncio.create_task(telemetria.enviar_alerta(f"🟢 <b>[PAPER TRADE]</b>\n{msg}"))

def guardar_historial_db(symbol, side, entry, exit_price, pnl, timestamp):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO historial_paper (symbol, side, entry, exit, pnl, time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (symbol, side, entry, exit_price, pnl, timestamp))
    conn.commit()
    conn.close()

def vigilar_posiciones_virtuales(symbol: str, precio_actual_ws: float):
    """
    Se ejecuta en cada tick de WebSocket (O(1) en RAM).
    Cierra la posición si toca TP o SL y la guarda en SQLite.
    """
    if symbol not in posiciones_activas:
        return
        
    pos = posiciones_activas[symbol]
    cerrar = False
    exit_price = 0.0
    pnl = 0.0
    
    if pos['side'] == 'buy':
        if precio_actual_ws <= pos['sl']:
            cerrar = True
            exit_price = pos['sl']
            pnl = -cfg.SL_PCT
            print(f"[PAPER] 🔴 STOP LOSS HIT: {symbol} a {precio_actual_ws:.4f}")
        elif precio_actual_ws >= pos['tp']:
            cerrar = True
            exit_price = pos['tp']
            pnl = cfg.TP_PCT
            print(f"[PAPER] 🏆 TAKE PROFIT HIT: {symbol} a {precio_actual_ws:.4f}")
    else: # short
        if precio_actual_ws >= pos['sl']:
            cerrar = True
            exit_price = pos['sl']
            pnl = -cfg.SL_PCT
            print(f"[PAPER] 🔴 STOP LOSS HIT (Short): {symbol} a {precio_actual_ws:.4f}")
        elif precio_actual_ws <= pos['tp']:
            cerrar = True
            exit_price = pos['tp']
            pnl = cfg.TP_PCT
            print(f"[PAPER] 🏆 TAKE PROFIT HIT (Short): {symbol} a {precio_actual_ws:.4f}")
            
    if cerrar:
        guardar_historial_db(
            symbol, 
            pos['side'], 
            pos['entry'], 
            exit_price, 
            pnl, 
            int(time.time() * 1000)
        )
        del posiciones_activas[symbol]
