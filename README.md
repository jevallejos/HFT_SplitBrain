# 🧠 HFT Split-Brain

Bot de Trading Institucional de Alta Frecuencia (HFT) especializado en cazar anomalías y flash-crashes de mercado con inteligencia artificial en tiempo real. 

El sistema utiliza una arquitectura "Split-Brain" asíncrona, disociando las tareas de rastreo de red, validación semántica mediante LLM (Gemini) y ejecución final a través de Bybit.

## 🚀 Arquitectura V2.0

La versión 2.0 actualiza el proyecto a un nivel completamente interactivo y HFT genuino:
- **Radar de Volatilidad (WebSockets):** Utiliza `ccxt.pro` para monitorear constantemente los ticks en tiempo real de los pares con mayor liquidez. Cálculos matemáticos incrementales O(1) sin depender de estructuras pasadas (Pandas) garantizando cero retardo.
- **Circuit Breakers (Guardián Sistémico):** Monitoreo global de BTC. Si Bitcoin colapsa (Z-Score < -4.0), las operaciones en Altcoins se congelan globalmente durante 30 minutos para evitar ser liquidado por un flash-crash macroeconómico.
- **Guardián de Time Drift:** Análisis continuo de la latencia para prever desfases de tiempo.
- **Escudo Semántico Paralelo (Gemini):** Evaluación On-Demand a través de Gemini 3.8 Flash para validar la moneda (evitar tokens envueltos en fraudes o rugs).
- **Simulador PNL (Paper Trading):** Operativa virtual que simula la ejecución en la bolsa interceptando al ejecutor. Incorpora validación O(1) de TP/SL en memoria y lo registra en una base local `sqlite3` para el backtesting en vivo.

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
pip install ccxt google-genai python-dotenv
```

### 2. Configurar el Entorno (Llaves API)
Debes crear un archivo `.env` en la raíz del proyecto y rellenarlo con tus credenciales:
```env
GEMINI_API_KEY=tu_api_key_de_gemini
BYBIT_API_KEY=tu_api_key_de_bybit
BYBIT_API_SECRET=tu_api_secret_de_bybit
```

### 3. Ejecutar el orquestador
```bash
python main.py
```

Por defecto, la ejecución arrancará en `MODO_PAPER = True` (simulación activada). Si deseas arriesgar dinero real, ajusta la constante dentro de `config_parametros.py`.

---
⚠️ *El uso en modo real implica un alto riesgo financiero. Se recomienda probar extensamente el Paper Trading antes de realizar transacciones en mainnet.*
