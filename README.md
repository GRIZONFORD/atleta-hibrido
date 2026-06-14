# 🧬 Atleta Híbrido OS

Sistema de **entrenamiento concurrente** basado en evidencia que reconcilia fuerza/hipertrofia
con resistencia de ultradistancia, con gating diario por **HRV** y **ACWR**, prescripción
nutricional y agenda inteligente. Objetivo del atleta: clasificar al **Maratón de Boston (≤ 3:00)**
maximizando masa muscular funcional.

> Estado: **v2.4.0** · App Streamlit + base de conocimiento científica · uso personal.

---

## 📂 Estructura

```
.
├── sync_orchestrator/        # 💻 La aplicación (arquitectura hexagonal, SOLID)
│   ├── domain/               # Núcleo puro: modelos (DTOs) + puertos (ABC)
│   ├── core/                 # Lógica: AcwrBrain (HRV+ACWR → decisión) + orquestador
│   ├── adapters/             # Garmin (real/mock) y Yazio (file/mock)
│   ├── services/             # Google Calendar (FreeBusy) + SlotFinder
│   ├── app/dashboard.py      # Dashboard Streamlit premium (modo oscuro)
│   ├── .streamlit/           # Tema oscuro nativo (config.toml)
│   └── requirements.txt      # Dependencias fijadas (lockfile)
├── research_base/            # 📚 Base de conocimiento científica (6 pilares, 54 refs)
├── plan_maestro_atleta_hibrido.md   # Plan de entrenamiento 24 meses
└── CONCURRENT_MIGRATION.md   # Changelog (Keep a Changelog)
```

## 🚀 Ejecutar en local

Desde la **raíz del repositorio** (así Streamlit lee el tema de `.streamlit/config.toml`,
igual que en la nube):

```powershell
sync_orchestrator\.venv\Scripts\streamlit run sync_orchestrator\app\dashboard.py
```
Abre http://localhost:8501. Sin conexión a Garmin, usa el selector de **simulación**
(Óptimo / Fatigado / Subentrenado).

### Conectar Garmin (opcional)
```powershell
cd sync_orchestrator
python setup_garmin.py          # login interactivo único → token cifrado local
```

### API REST (FastAPI) — opcional
El dominio se expone como API REST (adaptador de entrada). Útil para integraciones
y como contrato del futuro frontend Next.js.
```powershell
cd sync_orchestrator
.venv\Scripts\uvicorn api:app --reload
```
Docs interactivas: http://localhost:8000/docs · Endpoints: `/readiness/today`,
`/plan/today`, `/nutrition/targets`, `/trend`, `POST /calendar/schedule`.

## 🧠 Cómo decide el sistema

1. **Ingesta** — HRV (RMSSD/SDNN, motor clínico `hrv-analysis`) + carga aguda/crónica de Garmin.
2. **Cerebro** (`AcwrBrain`) — clasifica la zona cruzando **ACWR** (Gabbett 2016, sweet spot
   0.8–1.3) con la **HRV individual** (vs. baseline propio, no poblacional).
3. **Prescripción** — sesión + slot AM/PM (anti-interferencia mTOR/AMPK) + macros objetivo.
4. **Agenda** — `SlotFinder` ubica el bloque en un hueco libre (Google Calendar FreeBusy).

Todo el fundamento científico está en [`research_base/`](research_base/00_MOC.md).

## 🗺️ Hoja de ruta a "nivel app de paga" (uso personal)

| # | Sub-proyecto | Estado |
|---|---|---|
| 0 | Cimiento (git + .gitignore) | ✅ |
| 1 | UI premium + responsive móvil + deploy gratis + PWA | 🚧 en curso |
| 2 | Google Calendar real (OAuth end-to-end) | ⏳ |
| 3 | API FastAPI (desacoplar dominio del frontend) | ⏳ |
| 4 | Endurecimiento (tests, SQLite, fiabilidad token Garmin) | ⏳ |
| 5 | Frontend premium Next.js (futuro) | ⏳ |

## 🏗️ Principios de diseño
Arquitectura **hexagonal**: el dominio es puro (sin I/O), los adaptadores se inyectan
(Dependency Inversion), todo con type hints estrictos y degradación elegante.

## 📄 Licencia
Proyecto personal. Las referencias científicas pertenecen a sus autores (ver `_bibliography.md`).
