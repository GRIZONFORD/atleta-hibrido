---
title: "Pilar 2 — Cuantificación de Carga y Fatiga"
tags: [ACWR, HRV, RMSSD, training-zones, lactate, ventilatory-threshold]
updated: 2026-06-14
---

# 2️⃣ Cuantificación de Carga y Fatiga

> Volver al índice: [[00_MOC]] · Bibliografía: [[_bibliography]]

## 2.1 ACWR — Acute:Chronic Workload Ratio {#ACWR}

**Modelo (Gabbett, 2016):** relaciona la carga **aguda** (fatiga, ventana 7 días) con la
**crónica** (fitness/preparación, ventana ~28 días).

```
ACWR = Carga Aguda (media móvil 7 d) / Carga Crónica (media móvil 28 d)
```

| ACWR | Zona | Interpretación | Acción |
|---|---|---|---|
| **< 0.80** | 🔵 Subcarga | Fitness "desperdiciado", detraining, *spike* futuro riesgoso | Construir carga progresivamente |
| **0.80 – 1.30** | 🟢 "Sweet spot" | Equilibrio fitness-fatiga, riesgo lesivo mínimo | Mantener/progresar |
| **1.30 – 1.50** | 🟠 Límite | Acumulación rápida | Cautela, vigilar HRV |
| **> 1.50** | 🔴 Peligro | *Spike* agudo → riesgo lesivo elevado | **Descarga inmediata** |

**Cálculo recomendado:** usar **EWMA** (media móvil exponencial) en lugar de media simple, por
mejor sensibilidad a cargas recientes (**Williams et al., 2017**).

> ⚖️ **Rigor científico — la controversia ACWR:** el modelo ha recibido críticas metodológicas
> serias por acoplamiento matemático aguda↔crónica y elección arbitraria de ventanas
> (**Lolli et al., 2019**; **Impellizzeri et al., 2020**). **Conclusión honesta:** úsalo como
> *heurística de tendencia y bandera de spikes*, **no** como un umbral diagnóstico determinista.
> En esta plataforma se cruza siempre con [[#HRV|HRV individual]] para reducir falsos positivos.

**Implementación:** `AthleteDailySnapshot.acwr` y `AcwrBrain.ACWR_HIGH_RISK = 1.5` en
`../sync_orchestrator/`.

## 2.2 HRV — Variabilidad de la Frecuencia Cardíaca (RMSSD) {#HRV}

**Qué mide:** **RMSSD** (raíz cuadrada media de diferencias sucesivas entre intervalos R-R) refleja
el **tono parasimpático/vagal** → proxy de recuperación del sistema nervioso autónomo
(**Stanley, Peake & Buchheit, 2013**).

### Metodología de prescripción (Plews & Buchheit)
- **No** uses el valor diario aislado (ruidoso). Usa la **media móvil de 7 días de ln(RMSSD)**
  y su **coeficiente de variación (CV)** (**Plews et al., 2013**).
- Define el **Smallest Worthwhile Change (SWC)** ≈ media de 7 d ± 0.5 × DE individual.
- Mide en condiciones estandarizadas: **al despertar**, supino o sentado, mismo horario.

| Señal HRV (ln RMSSD 7d) | Estado autonómico | Decisión de entrenamiento |
|---|---|---|
| Dentro del SWC | Homeostasis | Plan normal |
| **↓ por debajo del SWC** 1 día | Estrés agudo | Mantener, vigilar |
| **↓ sostenida** ≥3 días (o caída >½ DE) | Simpático dominante / fatiga | **↓ intensidad** (no necesariamente volumen Z2); sin HIIT ni pliometría de alto impacto |
| **↑ CV elevada + tendencia errática** | Mala adaptación / no-función | Descarga, revisar sueño/nutrición |
| RMSSD alta y estable | Parasimpático, recuperado | Ventana para carga de calidad |

> En esta plataforma el `hrv_ratio = RMSSD / baseline_individual` con umbral `HRV_SUPPRESSED = 0.93`
> (RMSSD <93% del baseline propio → contraindicar alta intensidad). El motor clínico calcula
> RMSSD/SDNN reales con la librería `hrv-analysis` (Aura-healthcare) en el dashboard.

## 2.3 Zonas de entrenamiento — ancladas a fisiología, NO a %FCmax {#zonas}

Modelo de **5 zonas** anclado a **umbrales de lactato (LT1/LT2)** y **ventilatorios (VT1/VT2)**.
La distribución debe ser **polarizada ~80/20** (**Seiler, 2010**): ~80% del volumen por debajo
de VT1, ~20% por encima de VT2; minimizar la "zona gris".

| Zona | Frontera fisiológica | Lactato (mmol/L)* | RPE (/10) | Combustible dominante | Adaptación clave |
|---|---|---|---|---|---|
| **Z1 Recuperación** | < VT1 / < LT1 | < 1.5 | 1–2 | Grasa | Perfusión, recuperación |
| **Z2 Base aeróbica** | en torno a **LT1** (máx. oxidación de grasa) | **~1.5–2.0** | 2–3 | **Grasa (FatMax)** | **Biogénesis mitocondrial, flexibilidad metabólica** |
| **Z3 Tempo** | entre umbrales ("gris") | 2.0–3.5 | 4–6 | Mixto | Resistencia al lactato (uso cauto) |
| **Z4 Umbral** | en torno a **LT2 / MLSS / VT2** | **~3.5–4.5** | 7–8 | CHO | Aclaramiento de lactato, economía |
| **Z5 VO₂máx** | > VT2 | > 4.5–6+ | 9–10 | CHO/anaeróbico | Potencia aeróbica máxima |

*\*El lactato es **individual**: 4 mmol/L es una aproximación poblacional de MLSS, no una ley.
Idealmente se determina por **test incremental con lactímetro** o por umbrales ventilatorios.*

### Zona 2 — el concepto de San Millán & Brooks (2018)
Z2 = la intensidad de **máxima oxidación de grasas**, justo en/por debajo de **LT1** (~2 mmol/L),
donde la mitocondria (función MCT, lanzadera de lactato) se desarrolla con mínimo estrés simpático.
**Test de campo práctico:** poder mantener **conversación / respiración nasal**; si jadeas, te
fuiste a Z3. Crítico para construir la base aeróbica sin disparar la interferencia
[[01_physiology|AMPK]] excesiva.

## 2.4 Cuantificación de carga interna
- **sRPE (Foster):** carga sesión = **RPE (0–10) × duración (min)** → unidades arbitrarias (UA).
  Suma semanal alimenta el [[#ACWR|ACWR]]. Simple y validado (**Foster et al., 2001**).
- **TRIMP / Training Load de Garmin:** alternativa basada en FC; usada como `acute_load`/`chronic_load`.
- **Monotonía y Strain (Foster):** monotonía = media/DE de carga diaria semanal; strain = carga × monotonía.
  Monotonía alta + carga alta = bandera de sobreentrenamiento.

## Conexiones
- La decisión final (zona + spacing + macros) la integra [[03_periodization]] vía `AcwrBrain.evaluate`.
- El gating de macros por fatiga conecta con [[01_physiology#1.4 Dosificación de proteína]].

## Referencias de esta nota
Foster et al. (2001) · Seiler (2010) · Plews et al. (2013) · Stanley, Peake & Buchheit (2013) ·
Gabbett (2016) · Williams et al. (2017) · San Millán & Brooks (2018) · Lolli et al. (2019) ·
Impellizzeri et al. (2020). → Detalle en [[_bibliography]].
