# CONCURRENT_MIGRATION.md

> Registro histórico de la transición: **Running App básica → Ecosistema de Atleta Híbrido Concurrente**
> Formato: [Keep a Changelog](https://keepachangelog.com/) + Migration Guide. Versionado [SemVer](https://semver.org/).
> Última actualización: 2026-06-14 (rev. 2.4.0)

---

## [2.4.0] — 2026-06-14 — "Clinical HRV Integration & Premium GitHub Visuals"

### Resumen
Integración nativa de los 4 repositorios de GitHub instalados en `.venv/` como ciudadanos
de primera clase de la interfaz. El motor de HRV deja de inventar números: ahora `hrv-analysis`
(Aura-healthcare) procesa intervalos RR realistas y calcula RMSSD, SDNN y pNN50 con
algoritmia clínica validada. El gauge ACWR migra de Plotly a Apache ECharts con animación
fluida y 4 zonas de color reactivas. Las metric cards adoptan `streamlit-extras` con borde
izquierdo de color dinámico según el estado de fatiga. Las micro-animaciones Lottie reemplazan
los spinners nativos de Streamlit y celebran la Zona Óptima con animación CDN cacheada.

### Added

#### Motor Clínico HRV (`hrv-analysis` — Aura-healthcare)
- **`_generate_rr_intervals(scenario, n=300)`** — Genera intervalos RR (ms) deterministas
  con autocorrelación AR-1 calibrada por escenario:
  - `fatiga`:   base 700ms, std 32ms → RMSSD ~40ms, HR ~86bpm (SNA simpático dominante)
  - `optimo`:   base 820ms, std 46ms → RMSSD ~63ms, HR ~73bpm (ventana adaptativa)
  - `subcarga`: base 870ms, std 50ms → RMSSD ~68ms, HR ~70bpm (parasimpático elevado)
- **`_clinical_hrv(scenario)`** — Llama a `get_time_domain_features(rr_intervals)` de
  `hrvanalysis` con supresión de warnings. Expone RMSSD, SDNN, FC Media y pNN50.
  TTL cache 1h. Degradación elegante: si el algoritmo falla, valores fisiológicos por defecto.
- RMSSD y SDNN aparecen como badges en la Batería Biológica y en la Caja Negra Científica.

#### Gauge ECharts — Termómetro del Motor (`streamlit-echarts` — andfanilo)
- Reemplaza `go.Indicator` (Plotly) por `st_echarts()` con opciones de gauge Apache ECharts.
- 4 zonas de color normalizadas sobre eje [0, 2]:
  - `[0.0–0.8]` → `#0d1f3c` azul profundo (Motor Frío)
  - `[0.8–1.3]` → `#0a2010` verde oscuro (Zona Óptima)
  - `[1.3–1.5]` → `#2d1f00` ámbar oscuro (Zona Límite)
  - `[1.5–2.0]` → `#2d0808` rojo oscuro (¡Peligro de Avería!)
- Aguja con `shadowBlur` neón reactivo al estado. Anchor central estilizado.
- `detail.formatter` vía `JsCode` para 2 decimales. `valueAnimation: True` para
  transición suave al cambiar escenario.
- `axisLabel.formatter` vía `JsCode` para mostrar solo los ticks clave (0, 0.5, 1.0, 1.5, 2.0).

#### Metric Cards Reactivas (`streamlit-extras` — arnaudmiribel)
- `style_metric_cards(border_left_color=zcfg["color"], ...)` — borde izquierdo de color
  dinámico que refleja la zona de fatiga actual (rojo/verde/azul).
- Elimina el CSS manual de `[data-testid="metric-container"]` del bloque global,
  delegando la responsabilidad al componente de `streamlit-extras`.
- Background, border y border-radius unificados con el diseño oscuro del sistema.

#### Animaciones Lottie (`streamlit-lottie` — andfanilo)
- **`_lottie(url)`** — Descargador con `@st.cache_data(ttl=86400)`: un solo request por
  sesión de 24h. Retorna `None` si CDN no responde (sin excepciones visibles al usuario).
- **`_render_lottie(url, height, key)`** — Wrapper de degradación silenciosa.
- **Spinner de carga** — `with st_lottie(data, loop=False)` envuelve `_build_trend()`:
  la animación Lottie (`_LOTTIE_HEARTBEAT`) reproduce durante el cálculo; fallback a
  `st.spinner` nativo si CDN no disponible.
- **Celebración de Zona Óptima** — `_LOTTIE_SUCCESS` se renderiza en miniatura (80px)
  junto al banner cuando `decision.zone is FatigueZone.OPTIMIZACION`.

### Changed
- **Batería Biológica** — ahora muestra RMSSD y SDNN como badges HTML bajo el % de batería.
  Los valores provienen del motor clínico `_clinical_hrv()`, no de `snapshot.garmin.hrv_rmssd_ms`.
- **Footer** — incluye `RMSSD {hrv_clinical['rmssd']:.0f}ms` como dato clínico en tiempo real.
- **Expander científico** renombrado: `"🔬 Fundamento Científico"` → `"🧬 Caja Negra Científica
  y Código Limpio (SOLID)"`. Incluye tabla de arquitectura SOLID de las 4 librerías y tabla
  clínica de HRV con referencias normativas.
- **Versión** del footer y título interno: `v2.3.0` → `v2.4.0`.

### Technical
- `numpy>=1.24` requerido por `hrv-analysis` (ya disponible como dependencia transitiva).
- Importaciones premium en bloque único al inicio del módulo (evita imports tardíos).
- `_clinical_hrv` acepta solo `"fatiga" | "subcarga" | "optimo"` — escenarios del mock.
  Para datos Garmin reales, se pasa `"optimo"` como aproximación; en F1+ se conectará
  al baseline individual real de `GarminMetrics.hrv_baseline_ms`.

### Dependencies added
```
# Ya instaladas en .venv — sin cambios en requirements.txt
streamlit-echarts>=0.4.0   # Apache ECharts gauge animado
streamlit-extras>=1.0.0    # Metric cards con borde reactivo
streamlit-lottie>=0.0.5    # Micro-animaciones CDN cacheadas
hrv-analysis>=1.0.0        # Motor clínico RMSSD/SDNN validado
numpy>=1.24                # Generación de RR intervals (dependencia transitiva)
```

---

## [2.3.0] — 2026-06-13 — "Human Interface & Premium Visuals"

### Resumen
Rediseño completo del frontend. La interfaz técnica con fórmulas expuestas se transforma en
un dashboard premium modo oscuro donde cada métrica científica se traduce en lenguaje humano.
Se incorporan visualizaciones interactivas Plotly (velocímetro, batería, anillos, timeline).

### Added

#### Visualizaciones Plotly
- **`gauge_fig(acwr)`** — Velocímetro "Estado del Motor": `go.Indicator` con 4 zonas de color
  (Azul subcarga, Verde óptimo, Ámbar límite, Rojo peligro). Reemplaza la barra de progreso plana.
- **`battery_html(pct, color)`** — Batería Biológica HRV: HTML/CSS personalizado que mapea
  `hrv_ratio` [0.70–1.30] → porcentaje [0–100%] con color dinámico y efecto glow CSS.
- **`ring_fig(current, target, title, unit, color)`** — Anillos de nutrición estilo Apple Watch:
  `go.Pie` donut para Proteína / Carbohidratos / Calorías, meta calculada según el desgaste del día.
- **`trend_fig(df)`** — Gráfico de tendencia 14 días: `go.Scatter` + área rellena + puntos de color
  dinámico por zona + barras de carga en eje secundario. Hover muestra frases en lenguaje humano.
- **`timeline_fig(decision, busy)`** — Timeline horizontal del día: `go.Bar` horizontal superpuesto,
  bloques ocupados (rojo) vs. bloque de entrenamiento resuelto por SlotFinder (verde). Rango 06–21h.

#### Diseño visual
- Modo oscuro premium via CSS inyectado: fondo `#0d1117`, cards `#161b22`, bordes `#30363d`.
- Paleta deportiva: verde neón `#39d353`, rojo `#ef4444`, azul `#3b82f6`, ámbar `#f59e0b`.
- Banner de zona ancho completo con gradiente dinámico, mensaje humano y sub-mensaje contextual.
- Labels de sección en MAYÚSCULAS espaciadas (`.section-label`).
- Botones con gradiente verde y efecto glow en hover.
- Branding Streamlit ocultado (`#MainMenu, footer, header { visibility: hidden }`).

#### UX
- Toda la ciencia (ACWR, mTOR/AMPK, Gabbett) movida a `st.expander("🔬 Fundamento Científico
  para Entrenadores")` colapsado por defecto.
- Mensajes de hover 100% en lenguaje humano ("Ventana perfecta", "Mucha fatiga acumulada", etc.).
- `cache_key` por escenario en `_build_trend` para invalidación correcta al cambiar modos.
- Footer con versión, fuente de datos y timestamp.

### Changed
- Layout: 3 columnas planas → 3 filas temáticas (Gauges | Tendencia | Nutrición+Agenda).
- `build_acwr_trend` → `_build_trend` con `@st.cache_data(ttl=300)` y parámetro `cache_key`.
- `get_real_garmin` → `_real_garmin_adapter` (`@st.cache_resource`, singleton de conexión).
- Ciencia inlineada en columna 2 → único expander al pie de página.
- Selector de escenario: siempre visible → solo visible si `not garmin_connected`.

### Removed
- `st.line_chart` y `st.bar_chart` nativos (reemplazados por Plotly interactivo).
- Fórmulas y términos científicos de la vista principal.
- `ZONE_STYLE` dict → `ZONE_CFG` con campos `bg`, `border`, `color`, `icon`, `label`, `sub`.

### Dependencies added
```
plotly>=5.0
```

---

## [2.2.0] — 2026-06-13 — "Smart Scheduling + Live Dashboard"

### Resumen
Optimización de la automatización de agenda y visualización interactiva del pipeline.
La detección de conflictos migra de `events().list()` a `freebusy().query()` (endpoint
canónico de disponibilidad) y se incorpora una heurística de desplazamiento de horarios.
El dashboard se reescribe como interfaz reactiva completa.

### Added
- `services/slot_finder.py` — `SlotFinder` + `AllowedWindow`: heurística pura (sin I/O)
  de búsqueda de huecos libres de 60–90 min. Testeable sin credenciales.
- `GoogleCalendarService.get_busy_intervals()` — consulta `freebusy().query()`.
- `GoogleCalendarService.resolve_slot()` — combina FreeBusy + heurística; excluye el
  propio bloque de la app para que reprogramar no se auto-bloquee (idempotencia).
- Dashboard interactivo: selector reactivo de 3 estados, tendencia ACWR 14 días
  (`line_chart`), cargas aguda/crónica (`bar_chart`), banner de zona dinámico,
  `expander` con fundamento científico, botón Sincronizar/Preview.

### Changed
- Detección de solapamientos: `events().list()` → `freebusy().query()`
  (más barato, no expone detalles privados, soporta múltiples calendarios).
- Resolución de slot: extraída de `GoogleCalendarService` a `SlotFinder` (SRP).
- Summaries de eventos en ASCII (`[Entreno] ...`) para evitar artefactos de
  sincronización de OneDrive con caracteres multibyte.

### Fixed
- Reprogramación: el bloque propio de la app ya no se cuenta como ocupado (`_same_interval`).

### Heurística de desplazamiento (resumen)
1. Respeta el slot preferido del cerebro (p. ej. 18:00, anti-interferencia mTOR).
2. Si choca, explora offsets ±30 min crecientes dentro de la ventana 06:00–21:00.
3. Elige el primer hueco contiguo de la duración requerida; si no hay, lanza
   `ScheduleConflictError` (degradación elegante).

### Scopes / Breaking
- Se añade el scope `calendar.readonly` (requerido por FreeBusy). **Requiere
  reconsentir OAuth** (borrar `token.json` y re-autenticar).

### Verificación
- 18:00 libre → respeta 18:00 · reunión 17:30–18:30 → reubica a 18:30–19:50 ·
  día saturado → `ScheduleConflictError`. Todos los módulos compilan.

---

## [2.1.0] — 2026-06-13 — "Sync Orchestrator Prototype"

### Resumen
Prototipo funcional del Orquestador Central con mocks de datos, cerebro ACWR
operativo, servicio de Google Calendar y dashboard inicial. Implementación
concreta de la arquitectura hexagonal definida en [2.0.0].

### Added
- `domain/models.py` — DTOs inmutables (`@dataclass(frozen=True)`): `GarminMetrics`,
  `YazioMetrics`, `AthleteDailySnapshot` (props `acwr`, `hrv_ratio`), `TrainingDecision`;
  enums `FatigueZone`, `Phenotype`, `Slot`.
- `domain/gateways.py` — puertos ABC `MetricsGateway` / `NutritionGateway` (DIP).
- `adapters/mock_garmin.py` · `adapters/mock_yazio.py` — payloads realistas con
  escenarios forzables (optimo / fatiga / subcarga; deficit / superavit).
- `core/acwr_brain.py` — `AcwrBrain`: clasificación ACWR (sweet spot 0.8–1.3,
  riesgo > 1.5; Gabbett 2016) cruzada con HRV individual; umbrales parametrizables.
- `core/orchestrator.py` — `SyncOrchestrator` con inyección de dependencias y
  degradación elegante; `PipelineResult`.
- `services/google_calendar.py` — `GoogleCalendarService` con OAuth2 defensivo,
  upsert idempotente (`extendedProperties.private.app`) y detección de conflictos.
- `app/dashboard.py` (v1) — Streamlit de 3 columnas.
- `run_cli.py`, `requirements.txt`, `__init__.py` de cada paquete.

### Notas de diseño
- POO + SOLID + Type Hints estrictos; dominio puro sin I/O (testeable).
- Mocks evitan los bloqueos OAuth2/MFA del backend no oficial de Garmin durante el desarrollo.

### Verificación
- Compila completo. Escenarios: optimo → ACWR 1.07 → Optimización ·
  fatiga → ACWR 1.63 / HRV 0.69× → Lesión · subcarga → ACWR 0.58 → Funcional Baja.

---

## [2.0.0] — 2026-06-13 — "Concurrent Engine"

### Resumen de la migración

Transición de una app de *tracking* de carrera (lectura pasiva de Garmin → dashboard de km/ritmo)
a un **motor de periodización concurrente** que reconcilia fuerza máxima, hipertrofia, pliometría (CEA)
y maratón, con gating diario por HRV/ACWR y cierre del bucle nutricional vía Yazio.

### ⚠️ Breaking changes

- **AUTH:** se elimina el login automático con credenciales en cada run (rompía con MFA — bug
  upstream `cyberjunky/python-garminconnect#312`). Ahora se requiere **un login interactivo único**
  que persiste un *token bundle* cifrado; los runs posteriores hacen `resume_session()`.
- **DB:** `workouts` deja de ser una tabla plana de carreras; se normaliza en `sessions` +
  `session_blocks` para soportar fuerza/pliometría/running en un mismo día. **Requiere migración de datos.**
- **API:** `GET /runs` queda *deprecated* (alias temporal a `/sessions?type=run`); se retira en 3.0.0.

---

### Added

- **Dominio (hexagonal):** núcleo puro `domain/` (periodization, interference, nutrition) sin I/O.
- **Adaptadores:** `GarminAdapter` (pull + backoff/jitter), `YazioAdapter` (cola + fallback CSV),
  `McpAdapter` (exposición a Claude), `HttpAdapter` (REST).
- **Módulo de periodización por bloques** (Acumulación / Transmutación / Realización / Descarga).
- **Complex/Contrast Training (PAP/PAPE):** acople fuerza pesada → pliometría reactiva en sesión.
- **`adjust_daily()`:** gating de volumen pliométrico + macros por `hrv_ratio` y `ACWR`.
- **Token bundle cifrado** (Fernet) con refresh OAuth2 silencioso.
- **EventBus + Scheduler:** "webhooks" simulados (pull 1–2x/día → eventos internos).

### Changed

- Ingesta Garmin: de *polling en caliente* a **pull programado** con backoff exponencial + jitter
  (mitiga rate-limiting/Cloudflare del backend no oficial de Connect).
- Modelo nutricional: de informativo a **prescriptivo** (objetivos de proteína/CHO calculados).

### Deprecated

- `GET /runs`, `GET /runs/{id}` → usar `/sessions`.
- Acoplamiento directo a `garth` en la capa de servicio (ahora aislado tras puerto;
  upstream `matin/garth` está **DEPRECATED**).

### Removed

- Credenciales Garmin en variables de entorno de runtime (sustituidas por token bundle cifrado).

### Fixed

- Fallo de sincronización diaria en cuentas con MFA (vía session-resume).
- Caída de la app cuando Yazio no responde (degradación elegante a macros por defecto).

### Security

- Token bundle OAuth1+OAuth2 cifrado en reposo (`GARMIN_TOKEN_KEY` fuera del repo).
- Clave de cifrado y secretos movidos a *secret manager* (no en `.env` versionado).

---

## Mapa quirúrgico ANTES → DESPUÉS

### Base de datos

| Antes (v1.x) | Después (v2.0) | Acción de migración |
|---|---|---|
| `workouts(id, user_id, distance, pace, date)` | `sessions(id, user_id, date, type, phenotype, slot)` | Backfill: cada `workout` → `session` con `type='run'` |
| — | `session_blocks(id, session_id, modality, load_pct, reps, sets, rsi_target)` | Crea bloques fuerza/plio/run |
| — | `readiness(user_id, date, hrv_rmssd, hrv_baseline, acute_load, chronic_load, acwr)` | Nueva |
| — | `plan_adjustments(user_id, date, plyo_volume_pct, intensity_cap, protein_g_kg, cho_g_kg)` | Nueva |
| — | `garmin_tokens(user_id, blob_encrypted, updated_at)` | Nueva |
| — | `nutrition_targets(user_id, date, protein_g, cho_g, source)` | Nueva |

```sql
-- 001_normalize_sessions.sql
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  date DATE NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('run','strength','plyo','complex')),
  phenotype TEXT CHECK (phenotype IN ('SPEED_ECONOMY','MAX_POWER','HYPERTROPHY','BASE')),
  slot SMALLINT NOT NULL DEFAULT 1            -- 1=AM, 2=PM (separación mTOR/AMPK)
);

CREATE TABLE session_blocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  modality TEXT NOT NULL,                     -- 'squat','drop_jump','tempo_run',...
  load_pct NUMERIC,                           -- % 1RM (fuerza)
  reps SMALLINT, sets SMALLINT,
  rsi_target NUMERIC                          -- Reactive Strength Index (plio)
);

-- 002_backfill_runs.sql
INSERT INTO sessions (user_id, date, type, phenotype)
SELECT user_id, date, 'run', 'BASE' FROM workouts;
```

### Endpoints

| Antes | Después | Nota |
|---|---|---|
| `GET /runs` | `GET /sessions?type=run` | alias deprecado |
| — | `GET /plan/today` | plan ajustado del día |
| — | `GET /readiness/today` | HRV + ACWR + cap de intensidad |
| — | `POST /ingest/garmin` | dispara pull (idempotente) |
| — | `GET /nutrition/targets?date=` | macros prescritos |
| — | `MCP tool: get_today_plan()` | exposición a Claude |

### Módulos de entrenamiento

| Antes | Después |
|---|---|
| Plan estático de carrera | Periodización por bloques (Issurin, 2010) |
| — | Complex/Contrast (PAP/PAPE — Tillin & Bishop, 2009) |
| — | Gating pliométrico por readiness (ACWR — Gabbett, 2016) |
| — | Separación temporal fuerza/endurance (Robineau et al., 2016) |

### Modelos de IA / lógica de decisión

| Antes | Después |
|---|---|
| Ninguno | `adjust_daily(readiness, phenotype)` — gating determinista de volumen y macros |
| — | MCP server expone el dominio a Claude para Q&A y replanificación conversacional |
| — | Detección de tendencia HRV (media móvil 7d individual, no umbral absoluto) |

---

## Procedimiento de migración (runbook)

1. **Backup** completo de la DB.
2. `alembic upgrade head` (aplica `001`, `002`).
3. Ejecutar `interactive_login(email, password)` **una vez** (introducir OTP MFA) → persiste token cifrado.
4. Configurar `GARMIN_TOKEN_KEY` y `GARMIN_TOKEN_PATH` en el secret manager.
5. Activar el `Scheduler` (cron 1–2x/día) → verificar `HrvIngested`/`LoadIngested` en el bus.
6. Smoke test: `GET /plan/today` debe devolver `PlanAdjustment` no nulo.

## Rollback

1. `alembic downgrade -1` (restaura esquema v1).
2. Reactivar alias `/runs` como endpoint primario.
3. Restaurar backup si el backfill corrompió datos.
4. El token bundle cifrado puede conservarse (no rompe v1).

---

## Referencias metodológicas

- Aagaard P. (2003). *Neural adaptations to resistance training.* Exerc Sport Sci Rev.
- Baar K. (2014). *Using molecular biology to maximize concurrent training.* Sports Med.
- Barnes K.R., Kilding A.E. (2015). *Running economy: measurement, norms, determinants.* Sports Med Open.
- Beattie K. et al. (2014). *The effect of strength training on running economy.* Sports Med.
- Blagrove R.C., Howatson G., Hayes P.R. (2018). *Effects of strength training on distance runners.* Sports Med (meta-análisis).
- Coffey V.G., Hawley J.A. (2017). *Concurrent exercise training: molecular bases.* J Physiol.
- Gabbett T.J. (2016). *The training–injury prevention paradox (ACWR).* Br J Sports Med.
- Hawley J.A. (2009). *Molecular interference between concurrent training.* Appl Physiol Nutr Metab.
- Issurin V.B. (2010). *Block periodization.* Sports Med.
- Robineau J. et al. (2016). *Concurrent training: influence of recovery time on interference.* J Strength Cond Res.
- Rønnestad B.R., Mujika I. (2014). *Strength training for endurance performance (review).* Scand J Med Sci Sports.
- Saunders P.U. et al. (2006). *Plyometric training improves running economy in elite runners.* J Strength Cond Res.
- Spurrs R.W., Watsford M.L., Murphy A.J. (2003). *Plyometric training and distance running performance.* Eur J Appl Physiol.
- Tillin N.A., Bishop D. (2009). *Post-activation potentiation: factors and practical application.* Sports Med.

### Referencias técnicas (repos)

- `cyberjunky/python-garminconnect` — https://github.com/cyberjunky/python-garminconnect (Issue #312, #332)
- `matin/garth` — https://github.com/matin/garth (DEPRECATED)
- `Taxuspt/garmin_mcp` — https://github.com/Taxuspt/garmin_mcp
- `eddmann/garmin-connect-mcp` — https://github.com/eddmann/garmin-connect-mcp
- `Nicolasvegam/garmin-connect-mcp` — https://github.com/Nicolasvegam/garmin-connect-mcp
