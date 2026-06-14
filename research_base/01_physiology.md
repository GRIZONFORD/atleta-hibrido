---
title: "Pilar 1 — Fisiología de la Interferencia Molecular"
tags: [mTORC1, AMPK, PGC-1alpha, interference, protein-synthesis, spacing]
updated: 2026-06-14
---

# 1️⃣ Fisiología de la Interferencia Molecular (AMPK ↔ mTORC1)

> Volver al índice: [[00_MOC]] · Bibliografía: [[_bibliography]]

## 1.1 Las dos vías maestras

| Vía | Sensor de | Estímulo activador | Salida adaptativa | Efectores clave |
|---|---|---|---|---|
| **mTORC1** | Disponibilidad energética/AA y tensión mecánica | Fuerza pesada + leucina + insulina | ↑ Síntesis Proteica Muscular (MPS) → hipertrofia | p70S6K1, 4E-BP1, rpS6 |
| **AMPK** | Déficit energético (↑ AMP:ATP), ↓ glucógeno | Resistencia (volumen aeróbico) | ↑ Biogénesis mitocondrial, oxidación de grasas | PGC-1α, ACC, TSC2 |

**El conflicto (el "switch molecular"):** AMPK activada fosforila **TSC2** y el componente
**Raptor** de mTORC1, inhibiéndolo directamente. Es decir, la señal de "estoy sin energía"
(resistencia) **apaga** la señal de "construye músculo" (fuerza). Formalizado como hipótesis
del *AMPK–PKB(Akt) switch* por **Atherton et al. (2005)**, sobre la observación original de
interferencia de **Hickson (1980)**. Revisión molecular moderna: **Coffey & Hawley (2017)**;
**Hawley (2009)**.

> 🔑 **Matiz crítico (Murach & Bagley, 2016):** la interferencia molecular aguda **NO se traduce
> obligatoriamente en menor hipertrofia crónica** si la frecuencia, el volumen aeróbico y la
> recuperación se gestionan. La hipertrofia se compromete sobre todo con **alto volumen de
> resistencia, modalidad de impacto (correr > pedalear) y proximidad temporal**.

## 1.2 Magnitud de la interferencia — qué dice el meta-análisis

Según **Wilson et al. (2012)** (meta-análisis, JSCR), el decremento se escala con la dosis aeróbica:

| Variable de resistencia | Efecto sobre hipertrofia/fuerza | Implicación práctica |
|---|---|---|
| **Modalidad** | Correr interfiere > pedalear (componente excéntrico/impacto) | Priorizar bici/elíptica en días de fuerza pesada |
| **Frecuencia** | >3 sesiones aeróbicas/sem amplifica interferencia | Limitar solapamientos de alta frecuencia |
| **Duración** | Sesiones aeróbicas largas (>45–60 min) deprimen MPS más tiempo | Acortar el aeróbico en días de hipertrofia |
| **Intensidad** | HIIT interfiere con fuerza máxima; Z2 interfiere menos con hipertrofia | Casar Z2-largo lejos de fuerza máxima |

## 1.3 Matriz de spacing temporal (mitigación)

La supresión de mTORC1 post-aeróbico dura **~1–6 h**. La separación reduce el solapamiento de
señales (**Baar, 2014** `[PRÁCTICA-MOLECULAR]`; **Robineau et al., 2016** mostró que **≥6 h**
de recuperación intersesión preserva más adaptación de fuerza que <6 h).

| Escenario de programación | Interferencia esperada | Recomendación |
|---|---|---|
| Aeróbico **inmediatamente** antes de fuerza | 🔴 Alta | **Evitar** (mTORC1 pre-suprimido + fatiga) |
| Misma sesión, fuerza → aeróbico | 🟠 Media | Aceptable si el objetivo del día es resistencia |
| Mismo día, separado **6–8 h** (Fuerza AM / Run PM) | 🟢 Baja | **Óptimo operativo** para Sebas |
| **Días alternos** (fuerza y resistencia en días distintos) | 🟢 Mínima | Ideal cuando el volumen lo permite |
| Separación **>24 h** | ⚪ Nula | Solo viable con baja frecuencia semanal |

> **Regla de oro operativa:** *Fuerza/Hipertrofia → mínimo 6 h → Sesión aeróbica.* Implementada
> en el dominio como el campo `slot` (AM=1/PM=2) en `../sync_orchestrator/domain/models.py`.

## 1.4 Dosificación de proteína (proteger la MPS)

Basado en **Morton et al. (2018)** (meta-análisis BJSM) y **Phillips & Van Loon (2011)**:

| Parámetro | Dosis precisa | Fuente |
|---|---|---|
| Total diario (atleta de fuerza) | **1.6–2.2 g/kg/día** | Morton et al. (2018) |
| Por toma (maximizar MPS) | **0.3–0.4 g/kg** (~0.31 g/kg óptimo) | Moore et al. (2009); Morton et al. (2018) |
| Umbral de **leucina** por bolo | **~2.5–3.0 g** (dispara mTORC1 vía Sestrin/leucil-tRNA) | Phillips (2011) |
| Distribución | **4 tomas** equiespaciadas (cada 3–4 h) | Areta et al. (2013) |
| Caseína pre-sueño | **30–40 g** (MPS overnight) | Res et al. (2012); Snijders et al. (2015) |

**Aplicado a Sebas (60 kg):** objetivo **96–132 g/día**, en tomas de **~20–24 g** (≥2.5 g leucina c/u).

## 1.5 Reposición de glucógeno (recargar AMPK sin matar mTORC1)

La depleción de glucógeno es un **activador potente de AMPK** (Bartlett, Hawley & Morton, 2015).
Para el día híbrido en que quieres **hipertrofia**, no entrenes "train-low": rellena.

| Ventana | Dosis de carbohidrato | Fuente |
|---|---|---|
| Recarga rápida (post-run, <4 h al próximo estímulo) | **1.0–1.2 g CHO/kg/h** durante 4 h | Burke et al. (2017); Jentjens & Jeukendrup (2003) |
| Diario en fase de carga aeróbica alta | **5–7 g/kg/día** (moderado) a **6–10 g/kg/día** (alto) | Burke et al. (2011) |
| Co-ingesta proteína+CHO post-ejercicio | Añadir **0.3 g/kg proteína** acelera resíntesis y MPS | — |

> 🔬 **Periodización de CHO ("fuel for the work required"):** entrena con **alta disponibilidad**
> las sesiones de calidad (intervalos, fuerza pesada) y reserva el "train-low" selectivo solo para
> rodajes Z2 de baja intensidad si el objetivo puntual es maximizar señal mitocondrial
> (Impey et al., 2018). En fase de hipertrofia, **prioriza disponibilidad**.

## Conexiones
- El gating de macros por fatiga vive en [[02_load_and_fatigue#HRV]] y se ejecuta en `AcwrBrain._prescribe`.
- El reparto AM/PM se decide en [[03_periodization#Microciclo]].

## Referencias de esta nota
Hickson (1980) · Atherton et al. (2005) · Hawley (2009) · Wilson et al. (2012) ·
Areta et al. (2013) · Baar (2014) · Bartlett, Hawley & Morton (2015) · Murach & Bagley (2016) ·
Coffey & Hawley (2017) · Burke et al. (2017) · Morton et al. (2018) · Impey et al. (2018) ·
Robineau et al. (2016). → Detalle en [[_bibliography]].
