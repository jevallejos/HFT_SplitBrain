# INFORME DE ARQUITECTURA V3.0 - HFT SplitBrain

**Destinatario:** Google Gemini Pro Deep Think (IA Analista Principal)
**Objetivo del Informe:** Contextualizar los cambios estructurales profundos realizados en la versión 3.0 para permitir futuros análisis y continuaciones sin pérdida de contexto.

---

## 1. RESUMEN DE LA ACTUALIZACIÓN V3.0
El bot HFT (High Frequency Trading) ha evolucionado desde una dependencia total de la API de Gemini para la evaluación semántica (la cual sufría de Timeouts y errores 503 por rate limits), hacia un ecosistema más robusto, veloz y monitoreable.

Las principales refactorizaciones se centran en:
1. **Sustitución de Hardware Cognitivo:** Migración del cerebro semántico ("Escudo") hacia las LPU de **Groq**.
2. **Implementación del Sistema Nervioso (Telemetría):** Creación de un notificador de estado en tiempo real vía Telegram.

---

## 2. CAMBIOS EN LA ARQUITECTURA

### 2.1. Escudo Semántico (Módulo 2)
- **Tecnología anterior:** Google GenAI (Gemini 1.5 Flash).
- **Tecnología actual:** `groq.AsyncGroq` operando sobre Llama/GPT-OSS (`openai/gpt-oss-20b`).
- **Motivación:** Reducción drástica del TTFT (Time To First Token) de ~3-5 segundos a < 1 segundo (promediando ~750ms).
- **Manejo de Errores:** Implementación de `try/except` envolventes para evitar que las caídas de API externas bloqueen el loop principal de trading. Si Groq falla, el Escudo devuelve `False` (RECHAZADO) por seguridad.

### 2.2. Sistema de Telemetría (Módulo 4)
- **Nuevo Archivo:** `4_telemetria_telegram.py`.
- **Librería Utilizada:** `aiohttp` (para peticiones no bloqueantes).
- **Función:** Envío de logs y eventos críticos (Apertura de órdenes, Activación del Cortacircuitos, Errores graves) directamente al canal privado de Telegram del administrador.
- **Implementación en el Main:** Se envuelven las llamadas en `asyncio.create_task()` en `main.py` y `0_simulador_pnl.py` para asegurar que la notificación HTTP no pause bajo ninguna circunstancia el procesamiento de ticks de Bybit.

### 2.3. Entorno y Configuración (`config_parametros.py`)
- Se integró la lectura dinámica de variables sensibles vía `.env` usando la librería `python-dotenv`.
- Se han introducido tres nuevas variables críticas:
  - `GROQ_API_KEY`
  - `TELEGRAM_TOKEN`
  - `TELEGRAM_CHAT_ID`

### 2.4. Entorno de Validación Aisdalo
- Se diseñó el script `test_apis.py` como un entorno aséptico para probar los endpoints de red sin comprometer lógica de trading.

---

## 3. INSTRUCCIONES PARA LA IA SUPERVISORA
Cuando asumas el control de este código, ten en cuenta las siguientes restricciones y convenciones vigentes:
1. **Asincronía Obligatoria:** Todo I/O de red (Telegram, Bybit, Groq) **DEBE** permanecer asíncrono y no bloqueante.
2. **Gestión de Riesgo:** El "Escudo" debe fallar de forma segura (`fail-safe`). Ante la duda o excepción, se rechaza la moneda.
3. **Módulo Importable:** Cualquier nuevo módulo numérico (ej: `4_telemetria...`) que requiera importarse dinámicamente deberá referenciarse cuidadosamente o usando `importlib` de ser necesario, aunque en V3 la arquitectura permite el uso estandarizado.

**Fase Actual:** Validación finalizada con éxito (Código HTTP 200 en Telegram y Respuesta Válida en Groq). Listo para despliegue en Testnet (Paper Trading).
