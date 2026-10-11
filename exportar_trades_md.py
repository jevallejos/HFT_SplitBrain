import sqlite3
import datetime

DB_NAME = 'paper_trading.db'
OUTPUT_FILE = 'TRADES_HISTORIAL.md'

def exportar_trades():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Verificar si la tabla existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historial_paper'")
    if not cursor.fetchone():
        print("La base de datos aún no tiene historial registrado.")
        conn.close()
        return

    cursor.execute("SELECT id, symbol, side, entry, exit, pnl, time FROM historial_paper ORDER BY time DESC")
    trades = cursor.fetchall()
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# 📊 Historial de Operaciones (Paper Trading)\n\n")
        f.write("| ID | Símbolo | Tipo | Precio Entrada | Precio Salida | PnL (%) | Fecha (UTC) |\n")
        f.write("|----|---------|------|----------------|---------------|---------|-------------|\n")
        
        for t in trades:
            t_id, symbol, side, entry, exit_p, pnl, timestamp = t
            fecha = datetime.datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
            
            # Formatear el PnL
            emoji = "🟩" if pnl > 0 else "🟥"
            pnl_str = f"{pnl*100:.2f}% {emoji}"
            
            f.write(f"| {t_id} | {symbol} | {side.upper()} | {entry:.6f} | {exit_p:.6f} | {pnl_str} | {fecha} |\n")
            
    print(f"✅ Historial exportado exitosamente a {OUTPUT_FILE}")
    conn.close()

if __name__ == "__main__":
    exportar_trades()
