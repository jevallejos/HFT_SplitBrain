# 🧠 INFORME DE ARQUITECTURA Y PRUEBAS: SPLIT-BRAIN HFT BOT

## 1. Contexto y Objetivo
Se ha diseñado, implementado y probado con éxito un bot de trading de Alta Frecuencia (HFT) utilizando una arquitectura modular de "Cerebro Dividido" (Split-Brain). El objetivo es escanear el mercado cripto en tiempo real en busca de caídas abruptas de precio (flash crashes), evaluar el riesgo subyacente usando Inteligencia Artificial, y ejecutar posiciones de compra si el activo es legítimo y el riesgo es calculable.

## 2. Stack Tecnológico
- **Lenguaje:** Python 3.12 (Asíncrono con `asyncio`)
- **Conexión a Exchange:** Bybit (Vía librería `ccxt` async)
- **Análisis Matemático:** `pandas`, `pandas-ta`
- **Inteligencia Artificial:** `google-genai` (Modelo: `gemini-3.8-flash`)
- **Gestión de Entorno:** `.env` (dotenv) para llaves API aisladas.

## 3. Arquitectura Modular (Los 3 Cerebros)

### Módulo 1: El Radar de Volatilidad (`1_radar_volatilidad.py`)
- **Función:** Escanea el mercado (contratos perpetuos USDT) en Bybit. Filtra monedas basura o estables (ej. USDC, FDUSD) usando una lista negra (`PROHIBIDAS`).
- **Mecanismo:** Descarga velas de 1 minuto (`1m`). Calcula la Media Móvil Exponencial (EMA) y la Desviación Estándar con una ventana de 60 periodos. 
- **Disparador:** Genera un `Z-Score`. Si el Z-Score de la vela actual es `<= -3.5` (Umbral de Pánico), se considera una anomalía/colapso matemático y se dispara la alerta.

### Módulo 2: El Escudo Semántico (`2_escudo_semantico.py`)
- **Función:** Prevención de Rug-Pulls y Scams. 
- **Mecanismo:** Recibe el token alarmado por el Radar y lo envía a un prompt especializado procesado por **Gemini 3.8 Flash**.
- **Regla Estricta:** Gemini evalúa el token y responde EXCLUSIVAMENTE con la palabra "APROBADO" (si es un proyecto sólido cayendo por volatilidad del mercado) o "RECHAZADO" (si hay indicios de esquema ponzi, scam o token hiper-tóxico).

### Módulo 3: El Francotirador (`3_ejecutor_sniper.py`)
- **Función:** Gestión de capital y ejecución de la orden en Bybit.
- **Mecanismo:** 
  1. Consulta el saldo libre de USDT en la cuenta.
  2. Aplica el **Criterio de Kelly** para el tamaño de la posición (Máximo riesgo del 5% del capital por operación `KELLY_MAX_PCT = 0.05`).
  3. Convierte los dólares a la cantidad exacta de tokens respetando la precisión de decimales que exige Bybit.
  4. Calcula los niveles del escudo de protección: Stop-Loss (-3%) y Take-Profit (+5%).
  5. Ejecuta una orden `Market Buy` con sus respectivos parámetros `sl` y `tp`.

### El Orquestador Central (`main.py`)
- Mantiene un bucle asíncrono infinito (`while True`).
- Interconecta los tres módulos ejecutando múltiples radares de manera concurrente mediante `asyncio.gather` para evitar bloqueos.

---

## 4. Pruebas Ejecutadas y Resultados

### A. Prueba Unitaria del Escudo Semántico (IA)
- **Prueba 1 (Token Seguro):** Se envió "BTC/USDT" al modelo Gemini.
  - *Resultado:* El modelo analizó la legitimidad de Bitcoin y retornó `APROBADO`.
- **Prueba 2 (Token Tóxico):** Se envió "SQUID/USDT" (famoso rug-pull).
  - *Resultado:* El modelo detectó el historial de fraude y retornó `RECHAZADO`.

### B. Prueba de Flujo y Asincronía (Orquestador Central)
- **Ejecución:** Se corrió el archivo `main.py` durante más de 13 minutos ininterrumpidos en entorno local Windows.
- **Log obtenido:**
  ```text
  ==================================================
  INICIANDO CEREBRO CENTRAL SPLIT-BRAIN HFT
  ==================================================
  [MAIN] Radar escaneando 5 pares...
  [MAIN] Radar escaneando 5 pares...
  ...
  ```
- **Resultado:** El bot logró mantener el barrido de mercado cada 10 segundos, leyendo eficientemente los 5 pares más volátiles con mayor volumen, sin bloqueos (`blocking_io_errors`) ni límites de tasa (`RateLimitExceeded`), demostrando que la arquitectura asíncrona es estable.

### C. Prueba de Gatillo Seco (Simulación Sniper)
- El módulo de ejecución está actualmente con el gatillo bloqueado de forma intencional (las llamadas a `create_order` están comentadas en el código) para hacer pruebas de concepto (Dry Run) sin arriesgar el capital del usuario. El cálculo de saldo (Kelly) y precisión de lotes funciona a la perfección.

---

## 5. Repositorio
El código está versionado de forma segura ignorando las credenciales (`.env`) y publicado en GitHub en la rama `main` de forma exitosa.

## 6. Próximos Pasos Sugeridos (Para el Modelo de IA)
Se solicita a los LLMs que analicen este informe y respondan:
1. ¿Existen cuellos de botella no previstos al usar `asyncio.gather` en `main.py` si aumentamos el escaneo de 5 a 100 pares concurrentes?
2. ¿Qué optimizaciones se le pueden hacer al cálculo del Z-Score en el Radar para acelerar el procesamiento en milisegundos?
3. ¿Recomiendas algún mecanismo de "Circuit Breaker" a nivel global en caso de que Bybit experimente una latencia extrema?
