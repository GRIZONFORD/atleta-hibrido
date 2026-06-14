---
title: "Pilar 4 — Nutrición y Suplementación de Precisión"
tags: [nutrition, supplements, carbohydrate-periodization, RED-S, creatine, caffeine]
updated: 2026-06-14
---

# 4️⃣ Nutrición y Suplementación de Precisión

> Volver al índice: [[00_MOC]] · Bibliografía: [[_bibliography]] · Relacionada: [[01_physiology]]

## 4.1 Disponibilidad energética — el cimiento (antes que los macros)

**Energy Availability (EA)** = (Ingesta energética − Gasto del ejercicio) / masa libre de grasa (FFM).

| EA (kcal/kg FFM/día) | Estado | Consecuencia |
|---|---|---|
| **≥ 45** | Óptima | Adaptación y MPS plenas |
| 30 – 45 | Subóptima | Señalización anabólica comprometida |
| **< 30** | **LEA / RED-S** | ↓ testosterona, ↓ densidad ósea, ↓ tiroides, lesión, ↓ inmunidad |

> ⚠️ **Bandera para Sebas (60 kg, alto volumen aeróbico):** el atleta híbrido ligero es
> **población de riesgo de RED-S** (Síndrome de Deficiencia Energética Relativa en el Deporte).
> Vigilar peso, libido, sueño, FC reposo y HRV ([[02_load_and_fatigue#HRV]]). Consenso del COI:
> **Mountjoy et al. (2018, 2023)**.

## 4.2 Macronutrientes — objetivos por día (Thomas, Erdman & Burke, 2016 — ACSM/AND/DC)

| Macro | Rango | Cuándo el extremo alto | Notas |
|---|---|---|---|
| **Proteína** | **1.6–2.2 g/kg/día** | Fase hipertrofia / déficit | Ver dosis por toma en [[01_physiology#1.4 Dosificación de proteína]] |
| **Carbohidrato** | **3–10 g/kg/día** (periodizado) | Días de volumen aeróbico / calidad | Ver tabla 4.3 |
| **Grasa** | **0.8–1.5 g/kg/día** (≥20% kcal) | Días de bajo CHO | Nunca <0.5 g/kg (hormonal) |

## 4.3 Periodización de carbohidratos ("fuel for the work required", Impey et al. 2018)

| Tipo de día/sesión | CHO objetivo | Estrategia |
|---|---|---|
| Sesión de **calidad** (intervalos Z4–Z5, fuerza pesada) | **High availability**: 8–10 g/kg/día | Recargar 24 h antes; CHO intra-sesión si >75 min |
| **Rodaje largo Z2** (objetivo: señal mitocondrial) | **Train-low selectivo**: 3–5 g/kg | "Sleep-low" o ayuno ligero — solo si NO es día de hipertrofia |
| Día de **hipertrofia** | **Moderate-high**: 5–7 g/kg | Proteger mTORC1: NO entrenar con glucógeno bajo |
| Día de **descanso** | 3–5 g/kg | Mantenimiento |

**Intra-ejercicio (sesiones >75–90 min):** 30–60 g CHO/h; hasta **90 g/h** con mezcla
**glucosa:fructosa 2:1** (transportadores SGLT1+GLUT5) — **Jeukendrup (2014)**.

## 4.4 Suplementos — clasificados por nivel de evidencia (COI: Maughan et al., 2018)

### 🟢 Grupo A — evidencia sólida y mecanismo claro
| Suplemento | Dosis precisa | Para qué | Fuente |
|---|---|---|---|
| **Creatina monohidrato** | **3–5 g/día** (mantenimiento); carga opcional 20 g/d × 5–7 d | Fuerza, potencia, masa magra, recuperación; neutral para resistencia | Kreider et al. (2017) ISSN |
| **Cafeína** | **3–6 mg/kg**, 30–60 min pre | Rendimiento de resistencia y fuerza, RPE ↓ | Guest et al. (2021) ISSN |
| **Beta-alanina** | **3.2–6.4 g/día** × ≥4 sem | Tampón intramuscular (carnosina); esfuerzos 1–4 min | Trexler et al. (2015) ISSN |
| **Nitrato (remolacha)** | **6–13 mmol** (~310–560 mg), 2–3 h pre | Economía O₂, eficiencia mitocondrial | Jones (2014) |
| **Bicarbonato de sodio** | **0.2–0.4 g/kg**, 60–180 min pre | Tampón extracelular; alto-intensidad | Maughan et al. (2018) |

### 🟡 Grupo B — apoyo contextual / por déficit
| Suplemento | Dosis | Nota |
|---|---|---|
| **Vitamina D₃** | 1000–4000 UI/día (si déficit; medir 25(OH)D) | Función muscular/ósea/inmune — Close & Owens |
| **Omega-3 (EPA/DHA)** | 1–2 g/día | Modulación inflamatoria, posible apoyo MPS |
| **Whey / Caseína** | según gap de proteína | Whey post-ejercicio; caseína 30–40 g pre-sueño |
| **Colágeno + Vit C** | ver protocolo dedicado | → [[05_tendons_collagen]] |

> 🔴 **Grupo C/D (evidencia nula o riesgo):** la mayoría de "quemadores", BCAA aislados
> (inferiores a proteína completa), testosterone boosters. No recomendados.

## 4.5 Timing peri-entrenamiento (día doble Fuerza AM / Run PM)
```
AM Fuerza (07:00):
  Pre  (−45 min): 0.4 g/kg CHO + 20–25 g proteína
  Post (0–60 min): 25–30 g whey + 0.8–1.2 g/kg CHO
PM Run Z2 (18:00, ≥6 h después → protege spacing [[01_physiology]]):
  Pre (−90 min): comida mixta, CHO moderado
  Post: cena completa + caseína pre-sueño 30–40 g
```

## Conexiones
- Dosis de proteína y glucógeno detalladas en [[01_physiology]].
- El gating de macros por fatiga (proteína↑ en lesión, CHO↑ en carga aeróbica) se ejecuta en
  `AcwrBrain._prescribe` (`../sync_orchestrator/core/acwr_brain.py`).

## Referencias de esta nota
Jeukendrup (2014) · Jones (2014) · Trexler et al. (2015) · Thomas, Erdman & Burke (2016) ·
Kreider et al. (2017) · Jäger et al. (2017) · Maughan et al. (2018) · Mountjoy et al. (2018) ·
Impey et al. (2018) · Guest et al. (2021). → Detalle en [[_bibliography]].
