---
title: "Pilar 3 — Periodización Concurrente"
tags: [periodization, block-periodization, microcycle, mesocycle, session-order]
updated: 2026-06-14
---

# 3️⃣ Periodización Concurrente

> Volver al índice: [[00_MOC]] · Bibliografía: [[_bibliography]]

## 3.1 Concurrente puro vs. periodización por bloques

| Modelo | Definición | Ventaja | Limitación | Cuándo usar |
|---|---|---|---|---|
| **Concurrente puro** | Fuerza y resistencia se entrenan en el mismo microciclo, en paralelo | Mantiene ambas cualidades todo el año (necesario para el híbrido) | Interferencia crónica si se gestiona mal | Base/mantenimiento del híbrido (Viada `[PRÁCTICA]`) |
| **Bloques secuenciales** (Issurin, 2010) | Mesociclos con **una cualidad enfatizada** (acumulación → transmutación → realización), manteniendo la otra | Concentra la señal adaptativa, reduce interferencia simultánea | Riesgo de detraining de la cualidad no enfatizada | Picos de rendimiento (acercándose a Boston) |

> **Síntesis para Sebas:** **híbrido secuenciado** — bloques con énfasis rotativo (p. ej. bloque de
> hipertrofia con resistencia en *mantenimiento*, luego bloque de volumen aeróbico con fuerza en
> *mantenimiento*), nunca abandonando del todo ninguna vía. La fuerza requiere **menos volumen para
> mantenerse** que para ganarse (**Rønnestad & Mujika, 2014**), lo que facilita "aparcarla" en
> mantenimiento durante bloques de carga aeróbica alta.

## 3.2 Microciclo — plantilla semanal {#Microciclo}

Principios de diseño:
1. **Spacing** ≥6 h entre fuerza y resistencia el mismo día (ver [[01_physiology#Matriz de spacing|matriz]]).
2. **No** colocar HIIT/Z4–Z5 el día previo a fuerza máxima (fatiga del SNC compartida).
3. Rodaje **largo Z2** lejos de la sesión de fuerza pesada de piernas.
4. Distribución de intensidad **polarizada 80/20** ([[02_load_and_fatigue#zonas|Seiler]]).

| Día | AM (Slot 1) | PM (Slot 2, ≥6 h) | Énfasis del día |
|---|---|---|---|
| Lun | 💪 Fuerza tren inferior (pesado, RIR 1–2) | 🏃 Z2 30–40 min (opcional, bici si fatiga) | Fuerza |
| Mar | — | 🏃 Z4 umbral / intervalos | Resistencia calidad |
| Mié | 💪 Fuerza tren superior + core | 🏃 Z1–Z2 regenerativo | Fuerza |
| Jue | — | 🏃 Z2 medio | Aeróbico base |
| Vie | 💪 Full-body / potencia (contrast) | — | Fuerza/potencia |
| Sáb | 🏃 **Rodaje largo Z2** (progresivo) | — | Volumen aeróbico |
| Dom | Descanso / movilidad | — | Recuperación |

*RIR = Repeticiones En Reserva. Pesado en F1+ = RIR 1–2; en F0 = RIR 3–4 / RPE 6 (ver plan maestro).*

## 3.3 Mesociclo — modelo de carga ondulante con descarga {#Mesociclo}

Estructura **3:1** (tres semanas de carga creciente + una de descarga). La descarga reduce
**volumen ~40–50%** manteniendo algo de intensidad (preserva adaptaciones neurales).

| Semana | Carga relativa | ACWR objetivo | Nota |
|---|---|---|---|
| 1 | 100% (base del bloque) | ~1.0 | Reintroducción |
| 2 | +8–10% volumen | 1.0–1.2 | Regla del 10% (Nielsen et al., 2012) |
| 3 | +8–10% (pico del bloque) | 1.2–1.3 | Máxima carga del mesociclo |
| 4 | **–40 a –50%** | **0.8–1.0** | **Descarga / supercompensación** |

> La progresión de volumen no debe exceder **~10%/semana** para minimizar lesión por sobrecarga
> (**Nielsen et al., 2012**). El ACWR ([[02_load_and_fatigue#ACWR]]) es el control de seguridad.

## 3.4 Orden intra-sesión (si fuerza y resistencia DEBEN combinarse) {#orden}

Cuando el spacing no es posible y se entrena en una sola sesión:

| Orden | Efecto sobre fuerza/potencia | Efecto sobre resistencia | Recomendación |
|---|---|---|---|
| **Fuerza → Resistencia** | Mejor preservación de fuerza/potencia | Resistencia con algo de prefatiga | **Preferido** si la prioridad es fuerza/hipertrofia |
| **Resistencia → Fuerza** | Fuerza comprometida (mTORC1 presuprimido + fatiga) | Resistencia óptima | Solo si el día prioriza resistencia |

**Evidencia:** los meta-análisis modernos (**Schumann et al., 2022**; **Eddens et al., 2018**)
indican que el efecto del orden es **modalidad- y objetivo-dependiente** y de magnitud moderada;
el factor más influyente sigue siendo la **separación temporal y el volumen aeróbico total**, no
solo el orden. Manual de referencia: **Schumann & Rønnestad (2019)** `[LIBRO peer-reviewed]`.

## 3.5 Complex / Contrast Training (PAP/PAPE)
Acoplar un ejercicio de **fuerza pesada** (p. ej. sentadilla ~85–90% 1RM) con uno **pliométrico
reactivo** (p. ej. drop jump) explota la **potenciación post-activación** para mejorar economía de
carrera y reclutamiento (**Tillin & Bishop, 2009**; pliometría→economía: **Saunders et al., 2006**).
Implementado en el dominio como sesiones `type='complex'`.

## Conexiones
- El **slot AM/PM** y la **zona** salen de [[02_load_and_fatigue]] y se prescriben en `AcwrBrain`.
- La protección de la MPS en cada combinación viene de [[01_physiology]].
- Calendario operativo del atleta: `../plan_maestro_atleta_hibrido.md`.

## Referencias de esta nota
Saunders et al. (2006) · Tillin & Bishop (2009) · Issurin (2010) · Nielsen et al. (2012) ·
Rønnestad & Mujika (2014) · Eddens et al. (2018) · Schumann & Rønnestad (2019) ·
Schumann et al. (2022). → Detalle en [[_bibliography]].
