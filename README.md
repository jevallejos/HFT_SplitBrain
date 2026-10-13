# 🧠 HFT Split-Brain

Bot de Trading Institucional de Alta Frecuencia (HFT) especializado en cazar anomalías y flash-crashes de mercado con inteligencia artificial en tiempo real. 

El sistema utiliza una arquitectura "Split-Brain" asíncrona, disociando las tareas de rastreo de red, filtrado de microestructura de libro en tiempo real, validación semántica mediante LLM (Gemini/Groq) y ejecución final de baja latencia a través de Bybit.

---

## ⚡ Novedades V5.0: Arquitectura Cuántica OFI (Order Flow Imbalance)

La versión **5.0** erradica la **selección adversa** (*adverse selection*) y el peligro de comprar cuchillos cayendo (*falling knives*) mediante la inspección en $O(1)$ de la microestructura del Order Book en Nivel 1:

- **Filtro Cuántico de Microestructura (OFI):** Extrae directamente del flujo continuo de WebSockets (`ccxt.pro`) los volúmenes del mejor postor (`bidVolume`) y del mejor oferente (`askVolume`) sin latencia adicional.
  $$\text{OFI} = \frac{\text{vol}_{\text{bid}} - \text{vol}_{\text{ask}}}{\text{vol}_{\text{bid}} + \text{vol}_{\text{ask}}} \in [-1.0, 1.0]$$
- **Protección Automática ante Flujo Tóxico:** Si un activo entra en sobreventa estadística ($Z \le -3.5$) pero el ratio $\text{OFI} < -0.5$, el flujo es clasificado como **TÓXICO** (liquidaciones forzadas, ausencia de demanda pasiva) y el algoritmo aborta la operación inmediatamente (`continue`), protegiendo el capital.
- **Evidencia Empírica en Vivo:**
  ```text
  ⚠️ [MICROESTRUCTURA] ENA/USDT:USDT (Z-Score: -3.99). Flujo TÓXICO detectado (OFI: -0.99). Aboortando caída de cuchillo.
  ```
  *(El algoritmo descartó en microsegundos una compra perdedora en ENA a pesar de un Z-Score extremo de -3.99 al detectar un desbalance vendedor absoluto de -0.99).*

---

## 🚀 Características Principales del Sistema (V4.0 & V5.0)

- **Ejecución Límite Institucional (PostOnly):** Disparo de órdenes estrictamente *Maker* (`Limit PostOnly`) en Bybit para eliminar el slippage por volatilidad y garantizar comisiones de tipo *maker rebate*.
- **Radar de Volatilidad en Tiempo Real:** Utiliza `ccxt.pro` para monitorear concurrentemente los ticks de los pares de mayor volumen. Cálculos incrementales $O(1)$ de Z-Score y Media Móvil Exponencial (EMA) en RAM, prescindiendo por completo de Pandas.
- **Circuit Breakers (Guardián Sistémico):** Monitoreo global de BTC. Si Bitcoin colapsa ($Z \le -4.0$), las operaciones en Altcoins se congelan globalmente durante 30 minutos para evitar ser liquidado por un flash-crash macroeconómico.
- **Guardián de Latencia (Time Drift):** Análisis continuo de la latencia cliente-servidor para alertar sobre posibles retrasos en el flujo WebSocket.
- **Escudo Semántico Paralelo (Gemini / Groq):** Evaluación On-Demand a través de LLM para auditar noticias y estado del activo (evitar tokens envueltos en exploits, hackeos o rug pulls).
- **Simulador PNL (Paper Trading O(1)):** Operativa virtual que simula la ejecución en la bolsa interceptando al ejecutor. Incorpora validación $O(1)$ de TP/SL en memoria y registro persistente en base local `sqlite3`.
- **Telemetría Push vía Telegram:** Alertas en tiempo real enviadas directamente a dispositivos móviles ante inicios del sistema, trades ejecutados o activación de disyuntores.

---

## 📦 Estructura del Proyecto

- `main.py`: Orquestador principal asíncrono; coordina el radar WebSocket, el guardián de latencia y los callbacks tácticos.
- `config_parametros.py`: Parámetros globales, umbrales de pánico, límite de OFI tóxico (`UMBRAL_OFI_TOXICO = -0.5`), gestión de riesgo y API keys.
- `1_radar_volatilidad.py`: Observador reactivo de WebSockets, cálculo incremental de Z-Score y filtro cuántico de microestructura OFI.
- `2_escudo_semantico.py`: Escudo Semántico impulsado por IA para análisis de sentimiento y validación de fundamentales.
- `3_ejecutor_sniper.py`: Francotirador institucional encargado de efectuar la ejecución en Bybit vía Limit PostOnly con resguardos automáticos de TP/SL.
- `0_simulador_pnl.py`: Motor de simulaciones en RAM y base de datos SQLite local para Paper Trading.
- `4_telemetria_telegram.py`: Cliente asíncrono para notificaciones y alertas push.
- `INFORME_ARQUITECTURA_4.0.md`: Documentación de transición a Fuego Real y ejecución Limit PostOnly.
- `INFORME_ARQUITECTURA_5.0.md`: Documentación técnica exhaustiva del filtro de microestructura OFI.

---

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
Crear un archivo `.env` en la raíz del proyecto y especificar las credenciales:
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

Por defecto, la ejecución arrancará en el modo configurado en `config_parametros.py` (`MODO_PAPER = True` para simulación en SQLite o `MODO_PAPER = False` para Fuego Real en cuenta real Bybit).

---
⚠️ *Aviso de Riesgo: El trading de alta frecuencia en derivados de criptomonedas implica un riesgo financiero sustancial. Se aconseja operar extensamente en Paper Trading antes de habilitar la ejecución real.*
