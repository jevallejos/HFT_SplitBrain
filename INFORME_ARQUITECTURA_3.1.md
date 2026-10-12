# INFORME DE ARQUITECTURA V3.1 - HFT SplitBrain (Actualización de Producción)

**Destinatario:** Google Gemini Pro Deep Think (IA Analista Principal)
**Objetivo del Informe:** Proveer contexto sobre los ajustes finales del entorno y la confirmación de la operatividad del bucle asíncrono en Paper Trading, logrados en la V3.1.

---

## 1. ESTADO ACTUAL (VERSIÓN 3.1)
El sistema ha alcanzado exitosamente un estado operativo simulado ("Paper Trading") continuo. Se comprobó la interacción de los tres componentes primarios sin cuellos de botella bloqueantes críticos.

1. **Radar WebSockets (`1_radar_volatilidad.py`):** Monitorizando activamente símbolos de Bybit con alertas de Z-Score.
2. **Escudo Semántico (`2_escudo_semantico.py`):**
   - El modelo de Groq original fue actualizado debido a rotación de modelos (`decommissioned`).
   - **Modelo actual fijado:** `openai/gpt-oss-20b` (con compatibilidad probada y tiempos de latencia menores a 800ms).
   - Logra procesar decisiones asíncronamente en medio del flujo de WebSockets sin bloquear el motor.
3. **Francotirador / Ejecutor (`3_ejecutor_sniper.py` y `0_simulador_pnl.py`):**
   - Confirmada la interceptación de órdenes.
   - Posiciones de papel (ej. `NEAR/USDT:USDT` en `Side: buy`) abiertas correctamente en la base de datos `paper_trading.db`.
4. **Telemetría (`4_telemetria_telegram.py`):**
   - Alarmas enviadas exitosamente en segundo plano.

---

## 2. HALLAZGOS Y ADVERTENCIAS DURANTE LA PRUEBA (Para análisis futuro)
- **Latencias de Red (Circuit Breaker):** Durante el test, se detectaron repetidas alertas del Circuit Breaker por **Latencia alta (~1230ms)**. Aunque el motor no crasheó, esto indica un encolamiento en el flujo WS o en la latencia física al servidor de Bybit. Gemini Deep Think deberá revisar y optimizar la parametrización de `LATENCIA_MAX_MS` en el futuro o implementar estrategias de salto de ticks.
- **Entorno Limpio:** En ciertos despliegues de entorno, el usuario puede experimentar faltantes de `ccxt`, `groq` o `python-dotenv`. Al momento de pasar a Producción, será mandatorio un archivo `requirements.txt` consolidado.

---

## 3. OBJETIVO DE PRÓXIMA FASE (PRODUCCIÓN)
La V3.1 es el umbral para dejar el modo Paper Trading. El próximo paso de la IA Supervisora será:
1. Auditar la latencia de red recurrente (identificar si proviene del `asyncio.sleep`, de la validación del LLM, o del flujo de sockets).
2. Transicionar de `0_simulador_pnl.py` a órdenes Market reales en `3_ejecutor_sniper.py`.
