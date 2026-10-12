# 🧠 HFT Split-Brain

Bot de Trading Institucional de Alta Frecuencia (HFT) especializado en cazar anomalías y flash-crashes de mercado con inteligencia artificial en tiempo real. 

El sistema utiliza una arquitectura "Split-Brain" asíncrona, disociando las tareas de rastreo de red, validación semántica mediante LLM (Gemini) y ejecución final a través de Bybit.

## 🚀 Arquitectura V4.0 (Fuego Real)

La versión 4.0 marca el salto a Producción (Mainnet):
- **Ejecución Límite Institucional (PostOnly):** El bot ha desactivado el simulador en RAM (`MODO_PAPER = False`) y ahora dispara órdenes estrictamente *Maker* (Limit PostOnly) en Bybit. Esto elimina los riesgos de slippage (deslizamiento) y garantiza el cobro (rebates) de comisiones.
- **Motor LLM Groq:** El Escudo Semántico utiliza Llama 3 / GPT-OSS en Groq API. Esto soluciona cuellos de botella y ofrece latencias de validación HFT en tiempo real.
- **Sistema de Alertas Telegram Asíncrono:** Notificaciones push inmediatas y no bloqueantes de cada orden colocada o error crítico.
- **Radar de Volatilidad (WebSockets):** Utiliza `ccxt.pro` para monitorear los ticks de los pares líquidos con cálculos O(1).
- **Circuit Breakers (Guardián Sistémico):** Monitoreo global de BTC con congelamiento automático por caídas severas.

## 📦 Estructura del Proyecto
- `main.py`: Orquestador principal que levanta la red neuronal de WebSockets y administra los Callbacks.
- `0_simulador_pnl.py`: Motor de simulaciones (SQLite y RAM O(1)).
- `1_radar_volatilidad.py`: Observadores asíncronos WebSocket. Cálculos de Z-Score y Media Móvil Exponencial pura.
- `2_escudo_semantico.py`: Escudo Semántico impulsado por el SDK de `google.genai`.
- `3_ejecutor_sniper.py`: Francotirador encargado de efectuar la ejecución (o interceptarla al modo Paper) aplicando el criterio de inversión Kelly y resguardos automáticos de Take Profit/Stop Loss.
- `config_parametros.py`: Switch de configuración, control de riesgos y API keys.

## 🛠️ Instrucciones de Uso e Instalación

### 1. Clonar el repositorio y configurar entorno
```bash
git clone https://github.com/jevallejos/HFT_SplitBrain.git
cd HFT_SplitBrain
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar el Entorno (Llaves API)
Debes crear un archivo `.env` en la raíz del proyecto y rellenarlo con tus credenciales:
```env
# Intercambio
BYBIT_API_KEY=tu_api_key_de_bybit
BYBIT_API_SECRET=tu_api_secret_de_bybit

# Modelos LLM
GEMINI_API_KEY=tu_api_key_de_gemini
GROQ_API_KEY=tu_api_key_de_groq

# Telemetría
TELEGRAM_TOKEN=tu_token_bot_telegram
TELEGRAM_CHAT_ID=tu_chat_id
```

### 3. Ejecutar el orquestador
```bash
python main.py
```

Por defecto, la versión 4.0 opera en **Fuego Real** (`MODO_PAPER = False`). Si deseas volver a simular operaciones sin riesgo, ajusta la constante dentro de `config_parametros.py`.

---
⚠️ *El uso en modo real implica un alto riesgo financiero. Se recomienda probar extensamente el Paper Trading antes de realizar transacciones en mainnet.*
