# Knowledge Sidebar Filters v0

## Problema observado

La sidebar acumulaba conocimiento útil, pero una lista larga de assertions
era difícil de recorrer. La solución mantiene el archivo completo y añade
filtros locales, sin cambiar el mundo narrativo ni pedir nueva información a
la IA.

## Tipos usados

El payload existente de conocimiento ya distingue el tipo de assertion del
dominio:

- `Axiom`, mostrado como **Hecho**;
- `Deduction`, mostrado como **Derivado**.

No se han creado categorías nuevas ni se ha intentado deducir que una
assertion sea “personaje”, “lore” o “trama”. El estado (`Fixed` / `Open`) se
mantiene como una dimensión independiente del tipo.

## Diseño

La sección Conocimiento conserva sus grupos **Establecido** y **Abierto**.
Sobre ambos grupos aparecen botones de filtro con contador:

- **Todos**;
- una opción por cada tipo presente en el mundo.

Cada registro lleva una etiqueta discreta de tipo y conserva su origen. El
orden de los registros sigue siendo el recibido del mundo.

## Búsqueda

`Buscar conocimiento…` filtra en el navegador, sin llamadas al backend ni a
la IA. La búsqueda no distingue mayúsculas y minúsculas y se combina con el
filtro seleccionado. Si no queda ningún registro en un grupo, se muestra
“No hay elementos con este filtro.” Los controles y la búsqueda permanecen
activos durante la sesión de la página.

## Caso Paco / Laura

Con un mundo con múltiples assertions, **Todos** conserva el registro
completo. El filtro **Hecho** reduce la lista a axiomas y **Derivado** a
deducciones; escribir `Paco` reduce cualquiera de esas vistas a los textos
coincidentes. Al volver a **Todos** se recupera la lista completa porque el
filtrado sólo afecta a la presentación.

Los estados Open y Fixed continúan apareciendo en sus grupos originales y
ningún elemento se elimina del `SharedWorld`.

## Límites

- La sidebar filtra assertions, que son el conocimiento que ya exponía este
  panel; los `StoryObject` no se han convertido en registros nuevos.
- La taxonomía visible queda limitada a los tipos reales de assertion
  (`Axiom` y `Deduction`).
- No hay ordenamiento semántico, deduplicación, topología ni presión
  dramática en esta superficie.
- El filtro y la búsqueda son estado de la interfaz y no se persisten en el
  snapshot del mundo.

## Evaluación

**YES.** Para historias pequeñas y medianas, los filtros y la búsqueda hacen
que el archivo acumulativo sea recuperable sin ocultar conocimiento ni
convertir la sidebar en un segundo mapa. La solución escala por reducción
local de la lista, manteniendo la separación entre tipo, estado y contenido.

**Next real gap:** si la cantidad de assertions sigue creciendo, habrá que
observar si la paginación o una navegación temporal se vuelve necesaria;
todavía no hay evidencia para implementarla.
