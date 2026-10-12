# INFORME DE ARQUITECTURA V3.2 - HFT SplitBrain (Consolidación de Repositorio)

**Destinatario:** Google Gemini Pro Deep Think (IA Analista Principal) / Equipo de Desarrollo
**Objetivo del Informe:** Documentar las acciones de limpieza, reestructuración y unificación del código fuente para preparar el paso a entorno de Producción (Market Orders).

---

## 1. REESTRUCTURACIÓN DEL REPOSITORIO
Con el fin de mantener la base de código enfocada exclusivamente en los módulos críticos del bot HFT (High-Frequency Trading), se ejecutó una limpieza general de la raíz del proyecto.

### Módulos Principales (Raíz)
La carpeta raíz del proyecto ahora contiene estrictamente los componentes del Pipeline de Ejecución:
- `main.py` (Orquestador principal)
- `config_parametros.py` (Configuraciones globales y `.env`)
- `0_simulador_pnl.py` (Gestor de Paper Trading local)
- `1_radar_volatilidad.py` (Motor de WebSockets y Z-Score)
- `2_escudo_semantico.py` (Módulo Groq LPU de validación de noticias)
- `3_ejecutor_sniper.py` (Módulo de conexión REST API con Bybit)
- `4_telemetria_telegram.py` (Módulo asíncrono de alertas)

### Agrupación de Scripts de Diagnóstico
Los scripts utilizados previamente para pruebas de aislamiento y descubrimiento de fallos de API fueron movidos a la carpeta `/scripts/`:
- `scripts/descubrir_groq.py`
- `scripts/list_groq_models.py`
- `scripts/test_apis.py`
- `scripts/test_bybit.py`

## 2. POLÍTICAS DE CONTROL DE VERSIONES (GIT)
Se actualizó el archivo `.gitignore` y se purgó la caché de Git para asegurar que en la rama de producción (`main`) no se guarden archivos temporales o sensibles.
- **Archivos ignorados añadidos:** 
  - `*.log` (ej. `bot_hft.log`)
  - `*.db` / `*.sqlite3` (ej. `paper_trading.db`)
  - `__pycache__/` y `*.pyc`
  - `.env`
- **Resultados:** Eliminación del riesgo de corromper la base de datos de Paper Trading entre despliegues y reducción del tamaño del repositorio al dejar de trackear archivos de log en constante mutación.

## 3. CONSOLIDACIÓN DE DEPENDENCIAS
Se generó un archivo `requirements.txt` consolidado (mediante `pip freeze`) con todas las librerías necesarias para ejecutar la arquitectura V3.2, garantizando la reproducibilidad en nuevos entornos:
- `ccxt` (Conexión a Bybit)
- `groq` (Escudo Semántico)
- `aiohttp` / `asyncio` (Telemetría Telegram y Concurrencia)
- `python-dotenv` (Gestión de variables de entorno)

## 4. INTEGRACIÓN A PRODUCCIÓN (`main`)
Todos los cambios probados exitosamente en la rama `V3.0_pruebas_apis` (incluyendo la migración del modelo a `openai/gpt-oss-20b`) han sido fusionados (merge) a la rama `main` y etiquetados (`tag: v3.1`).

---

## 5. SIGUIENTE PASO ESTRATÉGICO
El repositorio ya se encuentra en un estado profesional, unificado y limpio, corriendo sobre la rama `main`. 

La arquitectura V4.0 consistirá en:
1. **Apagar Paper Trading:** Dejar de depender de `0_simulador_pnl.py` para la creación de transacciones virtuales.
2. **Conectar el Francotirador (`3_ejecutor_sniper.py`):** Configurar y habilitar la apertura de Market Orders (LONG/SHORT) en Bybit usando las API Keys reales a través del motor `ccxt`.
