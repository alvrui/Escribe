# Issue Identity / Current Attention v0

## Problema observado

La reevaluación podía producir varias veces el mismo hueco con textos
ligeramente distintos. Además, el selector original elegía siempre entre
Issues abiertos sin recordar que un foco antiguo podía dejar de ser el más
útil cuando la historia avanzaba.

La solución separa dos preguntas:

- **identidad:** ¿la propuesta es nueva, duplica un Issue activo o refina uno
  existente?
- **atención:** ¿el foco anterior se mantiene, se actualiza, cambia o no debe
  seleccionarse?

## Contrato de identidad

La comparación se realiza en la frontera AI, usando `AiContextPackage` y sus
handles efímeros. El modelo recibe los Issues `Open` y `Accepted` activos y
clasifica cada propuesta como `NEW`, `DUPLICATE` o `REFINES`, con el handle
del Issue existente cuando corresponde.

La aplicación valida estrictamente la respuesta. Una propuesta duplicada o
refinada no crea otro Issue; el hueco de suficiencia se redirige al ID del
Issue conservado. No se comparan textos con keywords ni se reparan
referencias. La rama de refinamiento conserva identidad y provenance, aunque
esta v0 todavía no sustituye el texto del Issue existente; esa formulación
histórica queda como una limitación explícita.

## Contrato de atención

La decisión de atención es local y efímera:

- `KEEP`: el foco anterior sigue siendo el adecuado;
- `UPDATE`: el mismo foco incorpora significado nuevo;
- `SHIFT`: otro Issue pasa a ser el foco;
- `NONE`: no se fuerza una pregunta.

La política recibe el contexto actual, los Issues activos, la nueva
propuesta y el foco anterior. No cambia `Open`, `Accepted` o `Resolved`, no
crea canon y no resuelve Issues. El foco seleccionado se guarda únicamente
en la capa de aplicación web y se limpia al crear o cargar un mundo.

## Flujo

```text
ModuleOutput
    ↓
Issue identity / attention policy (AI handles)
    ↓
remove duplicate proposal + remap sufficiency gap
    ↓
atomic SharedWorld application
    ↓
select current Issue
    ↓
Socrates / Presenter
```

Las funciones existentes sin política mantienen su comportamiento anterior,
por lo que los flujos de motor y tests offline siguen siendo compatibles.
La aplicación web configurada con OpenAI usa la política integrada.

## Evidencia offline

Los tests cubren que una propuesta marcada como duplicada reutiliza la
identidad existente, evita crear un clon, permite preguntar sobre el Issue
conservado y deja su estado `Open`. También cubren `NONE`: no se fuerza foco
ni pregunta. La conversión AI rechaza matches inexistentes y handles que no
sean Issues.

## Paco / fixture real

La secuencia normal y la alterada quedan preparadas para validación con el
modelo configurado. La política tiene información suficiente para distinguir
un foco anterior de un Issue nuevo cuando el contexto y la respuesta AI lo
justifican; no se ha añadido una prioridad por recencia ni una puntuación
dramática. El resultado real debe observarse con la instancia web y los
ocho textos, porque la decisión semántica pertenece al modelo.

## Autoridad y límites

El Issue original puede seguir abierto aunque deje de ser atención actual.
La política sólo clasifica identidad y relevancia efímera: no fija,
descarta, acepta, resuelve ni canoniza. Tampoco deduplica Issues `Resolved`
por defecto. Las respuestas AI inválidas se rechazan y no atraviesan la
frontera de handles.

## Evaluación

**PARTIALLY.** La infraestructura ya impide clones semánticos cuando la
política AI los identifica y permite que el foco deje de ser pegajoso sin
alterar autoridad. Los tests demuestran la separación; queda validar con la
secuencia Paco en uso real que el modelo produzca decisiones de atención
consistentes en los dos órdenes.

**Next real gap:** conservar de forma trazable una formulación refinada de un
Issue sin perder su identidad ni acumular versiones opacas.
