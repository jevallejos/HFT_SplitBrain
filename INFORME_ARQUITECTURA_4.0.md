# INFORME DE ARQUITECTURA V4.0 - HFT SplitBrain (Transición a Fuego Real)

**Destinatario:** Google Gemini Pro Deep Think (IA Analista Principal)
**Objetivo del Informe:** Documentar la implementación de la operativa real en mercado (Mainnet) a través del motor Limit PostOnly.

---

## 1. HITOS DE LA VERSIÓN 4.0
El hito principal de esta versión es la **desactivación definitiva del entorno de Paper Trading** (`MODO_PAPER = False`) y la conexión de la lógica de HFT directamente contra el libro de órdenes (Orderbook) de Bybit usando los fondos reales.

### Cambio Crítico: Ejecución Institucional Estricta
Se instruyó y cumplió el rediseño total de la función de ejecución dentro de `3_ejecutor_sniper.py`:
- **Prohibición de Órdenes Market:** Las órdenes a mercado son destructivas para el High-Frequency Trading debido a los deslizamientos (Slippage) de precio durante la alta volatilidad y a las costosas tarifas de tipo "Taker".
- **Limit PostOnly:** Se inyectó el parámetro `{'timeInForce': 'PostOnly'}` sobre una orden tipo `limit`. El bot ahora opera como proveedor de liquidez pasiva ("Maker").
  - Si la orden colisiona inmediatamente con el libro (se vuelve Taker), Bybit está instruido para **cancelarla** automáticamente, protegiendo el capital de comisiones altas.

## 2. GESTIÓN DE RIESGO Y CONTROL DE FALLOS (TELEMETRÍA)
Al entrar a operar con dinero real, el bloque de ejecución se encapsuló en un marco estricto `try/except`. 
La telemetría ahora asume un rol crítico:
- **Alerta Verde (Éxito):** Cuando la orden `Limit PostOnly` se coloca con éxito en el servidor de Bybit, un proceso asíncrono en segundo plano (`asyncio.create_task`) dispara la notificación a Telegram detallando el Precio y el ID de la orden.
- **Alerta Roja (Fallo Crítico):** Si la creación de la orden falla (por ejemplo, porque el precio "PostOnly" cruzó el spread, balance insuficiente, o las credenciales de API perdieron permisos), el bot reporta asíncronamente a Telegram para intervención humana inmediata.

## 3. ESTADO DEL REPOSITORIO Y DESPLIEGUE
- **Limpieza (Branch V4_produccion_fuego_real):** Se consolidó el repositorio en un branch de paso a producción final (`V4_produccion_fuego_real`), eliminando artefactos y pruebas antiguas en favor de una base HFT prístina.
- **README Actualizado:** La documentación oficial ya refleja el estatus de la V4.0 (Fuego Real) con requerimientos consolidados (`requirements.txt`) e instrucciones de `.env` completas.

## 4. RIESGOS PENDIENTES PARA EL PRÓXIMO SPRINT
Con la versión operativa y en mercado abierto, los analistas y modelos mayores deberán observar la interacción del *Time In Force: PostOnly*:
- ¿La constante volatilidad provoca que las órdenes sean canceladas con frecuencia antes de ser llenadas? 
- Si esto ocurre, el equipo deberá proponer algoritmos de "Chase" (perseguir precio) o un ligero spread matemático en el cálculo de `precio_actual`.
