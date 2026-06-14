---
title: "Base de Conocimiento — Atleta Híbrido"
type: MOC
tags: [hybrid-athlete, concurrent-training, MOC, evidence-based]
updated: 2026-06-14
---

# 🧬 Map of Content — Investigación del Atleta Híbrido

> Base científica curada para el desarrollo **concurrente** de fuerza/hipertrofia y
> resistencia de ultradistancia. Cada afirmación está anclada a evidencia indexada
> (ver [[_bibliography]]). Diseñada para Obsidian/Notion: navega con los `[[wikilinks]]`.

## ⚠️ Política anti-alucinación de esta base
- Todas las citas usan **enlaces de búsqueda PubMed** (autor + título), que siempre resuelven.
- **No se incluyen PMIDs ni DOIs numéricos exactos** porque un dígito erróneo apuntaría a un
  paper distinto: ese es el riesgo real de fabricación. Verifica el identificador en el enlace.
- Las fuentes de **practicantes** (libros, no peer-review) se marcan explícitamente como `[PRÁCTICA]`.

---

## Los 6 Pilares

### 1️⃣ [[01_physiology|Fisiología de la Interferencia Molecular]]
La guerra celular **AMPK vs. mTORC1**, el "switch molecular" (Atherton 2005), y las
estrategias de *spacing* (6–24 h) para que el running no apague la síntesis proteica.
Incluye tablas de dosificación de **proteína (g/kg)**, **umbral de leucina** y
**reposición de glucógeno (g CHO/kg/h)**.

### 2️⃣ [[02_load_and_fatigue|Cuantificación de Carga y Fatiga]]
**ACWR** (Gabbett 2016) con sus críticas metodológicas, **HRV-RMSSD** (Plews, Buchheit)
para el gating diario, y el sistema de **5 zonas** anclado a **lactato y umbrales
ventilatorios** (San Millán & Brooks, Seiler 80/20) — no a fórmulas de %FCmax.

### 3️⃣ [[03_periodization|Periodización Concurrente]]
Concurrente puro vs. **periodización por bloques** (Issurin 2010), plantillas de
**microciclo** (distribución semanal + spacing) y **mesociclo** (carga 3:1 con descarga),
y el debate del **orden intra-sesión** (Schumann 2022).

### 4️⃣ [[04_nutrition|Nutrición y Suplementación de Precisión]]
**Disponibilidad energética** y riesgo de **RED-S** (Mountjoy), macros periodizados,
**carbohidrato "fuel for the work required"** (Impey 2018) y suplementos **clasificados por
nivel de evidencia** (COI, Maughan 2018): creatina, cafeína, beta-alanina, nitrato, bicarbonato.

### 5️⃣ [[05_tendons_collagen|Tendones, Colágeno y Protocolo de Baar]]
El tejido conectivo adapta **más lento** que el músculo (causa #1 de lesión en F0). Protocolo
**15 g colágeno + 50 mg vit C, 30–60 min antes de cargar** (Shaw/Baar 2017), periodo refractario
de 6 h, y carga mecánica **HSR vs. excéntrico vs. isométrico** (Beyer 2015, Rio 2015).

### 6️⃣ [[06_plyometrics|Pliometría y Ciclo Estiramiento-Acortamiento]]
El **SSC** y la **economía de carrera** (Spurrs 2003, Saunders 2006), la métrica **RSI**,
progresión por **volumen de contactos** (intro 60–80 → avanzado 140) y la integración
**Complex/PAP**. Vinculada a la salud del tendón ([[05_tendons_collagen]]).

---

> 🔗 **Cadena de seguridad del tejido (F0):** [[06_plyometrics|Pliometría]] **carga** el tendón →
> [[05_tendons_collagen|Colágeno/Baar]] lo **protege** → [[04_nutrition|Nutrición]] aporta el **sustrato**
> (vit C, EA) → [[02_load_and_fatigue|ACWR/HRV]] **regula la dosis**. Todo encadenado.

## Mapa conceptual del conflicto

```
RESISTENCIA (correr)                    FUERZA (levantar)
   │ ↑ AMP:ATP, ↓ glucógeno                │ Tensión mecánica + Leucina
   ▼                                       ▼
 AMPK ───┤ inhibe (TSC2, Raptor) ├──►  mTORC1 ──► p70S6K / 4E-BP1
   │                                       │
   ▼                                       ▼
 PGC-1α                              Síntesis Proteica Muscular (MPS)
 (mitocondrias, ↑ VO2)               (hipertrofia, ↑ fuerza)
```
La interferencia es **transitoria (~1–6 h)** → el [[01_physiology#Matriz de spacing|spacing temporal]] la mitiga.

---

## Estado de aplicación al atleta (Sebas)
- **Fase actual:** F0 Reacondicionamiento — ver `../plan_maestro_atleta_hibrido.md`.
- **Implementación software:** el cerebro `AcwrBrain` (`../sync_orchestrator/core/acwr_brain.py`)
  operacionaliza el [[02_load_and_fatigue#ACWR|ACWR]] + [[02_load_and_fatigue#HRV|HRV ratio]] de esta base.

## Cómo citar dentro de las notas
Formato inline: `(Autor, Año)` → resuelto en [[_bibliography]].
