# Interpreter Local Reference Boundary v0

## Causa

Durante el bootstrap de una historia vacía, el modelo devolvió una referencia
local como si fuera persistente: `StoryObject:object_5`. `object_5` sólo es
un identificador provisional de la interpretación; no es un UUID ni puede
convertirse en `TargetRef` persistente. La respuesta se rechazaba antes de
aplicar nada.

## Contrato corregido

El schema estricto distingue ahora:

```json
{"existing_target":"StoryObject:<uuid>"}
{"new_story_object":"object_5"}
```

Las referencias existentes deben ser persistentes y estar presentes en el
contexto. Las propuestas nuevas deben apuntar a un `local_ref` declarado en
`story_objects`. Una referencia local nunca se acepta ni se repara como
`StoryObject:<local_ref>`.

```text
interpretation → local_ref temporal → review → governed apply → StoryObjectId
```

`SharedWorld`, CognitiveLoop y la semántica de bootstrap no cambian.

## Diagnóstico y logging

Se distinguen localmente `InvalidExistingReference` (por ejemplo,
`StoryObject:object_5`) e `InvalidLocalReferenceEncoding` (local_ref no
declarado). Los errores de `POST /api/interpret` se escriben en stderr como
`Taberna interpretation error: ...`, sin API keys, headers ni secretos.

## Tests offline

Se verificaron referencias persistentes válidas, referencias locales
estructuradas, mezcla existente/nueva, local_ref inexistente y duplicado,
rechazo de `StoryObject:object_5`, prompt y schema estrictos. Resultado:
207 tests pasados, 11 ignorados y 0 fallos.

## Validación real

Con `gpt-5.6-luna` y la clave cargada desde `zshrc`, se probó:

```text
Paco trabaja con Laura y Rafael. Laura dirige al equipo y Rafael lleva la
relación con el cliente.
```

Se obtuvieron 4 respuestas completas antes del límite temporal del entorno;
no se cuenta como una matriz formal de 5 runs. En las 4 respuestas, los
objetos nuevos usaron `object_1..object_5` como `new_story_object` y no
apareció ninguna referencia `StoryObject:object_N`. Queda pendiente repetir
un quinto run completo fuera de ese límite.

## Limitaciones

La validación general de referencias AI sigue siendo estricta y otras
referencias inválidas no relacionadas con local_ref quedan fuera de este
cambio. Tampoco se modificaron semantic fidelity, Context, grafo, Socrates ni
Presenter.

## Verificación

- `cargo fmt -- --check`: correcto.
- `cargo test --offline`: correcto.
- `cargo clippy --all-targets --all-features --offline -- -D warnings`:
  correcto.
- `node --check web/app.js`: correcto.
