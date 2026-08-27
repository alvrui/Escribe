# Visual Reasoning: Issues v1

## Resultado

El mapa de Taberna deja de representar los Issues sólo como un contador. La
proyección incluye nodos de tipo `Issue` y aristas explícitas que los conectan
con los StoryObjects afectados. El Issue continúa siendo el objeto original
del mundo proyectado: no se duplica, no se resuelve y no se modifica.

## Reglas

- `Open` y `Accepted` son visibles con `include_issues` activo.
- `Resolved` queda oculto por defecto.
- Un Issue sólo aparece si se asocia explícitamente a StoryObjects
  seleccionados, directamente o a través de una Assertion que los referencia.
- La arista conserva como evidencia la referencia real al Issue.
- `GraphNodeKind` distingue `StoryObject` de `Issue`; no se añadieron nodos
  para Assertions, Evaluations o Reactions.
- No se infieren relaciones por texto ni se añaden scores narrativos.

Las dimensiones continúan siendo `Characters`, `Lore` y `Plot`, con su
semántica anterior. Las relaciones narrativas siguen derivándose sólo de
Assertions con referencias explícitas a dos o más StoryObjects.

## UI

Los StoryObjects mantienen círculos. Los Issues aparecen como rombos con
`⚠`, y sus aristas son discontinuas y discretas. El grosor narrativo sigue
representando sólo `evidence_count`; los Issues representan atención
estructural, no importancia o drama.

Las aristas se pueden seleccionar: el inspector muestra elementos conectados,
texto de evidencia y conteos. Al seleccionar un Issue muestra texto, estado y
StoryObjects asociados. No hay edición ni acciones de autoridad.

## Fixture Paco

La fixture de Paco, Jefe, Proyecto y Cliente permite ver los dos Issues como
nodos y sus asociaciones explícitas. Los tests verifican nodos únicos,
referencias y evidencia válidas, estados conservados, orden determinista y
ausencia de mutación de `SharedWorld`.

## Limitaciones

1. No existe aún una señal estructural universal para conflicto o stake.
2. `Lore` y `Plot` siguen dependiendo de provenance explícita.
3. Issues sin asociación a StoryObjects seleccionados no aparecen como nodos.
4. No hay clustering, zoom, pan ni layout avanzado.
5. El inspector no llama al Presenter ni a IA.
6. No se añadió Socrates/bombilla.

La ampliación no modificó `SharedWorld`, CognitiveLoop ni la ontología
narrativa. La presión observada sigue siendo la clasificación conservadora
por provenance, que queda documentada sin heurísticas nuevas.

## Verificación

- `cargo fmt -- --check`: correcto.
- `cargo test --offline`: 208 pasados, 11 ignorados, 0 fallos.
- `cargo clippy --all-targets --all-features --offline -- -D warnings`:
  correcto.
- `node --check web/app.js`: correcto.
