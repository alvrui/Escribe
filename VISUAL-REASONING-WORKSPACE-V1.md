# Visual Reasoning Workspace v1

## Resultado

El grafo ya no es una sección inferior del workspace. El área central tiene
dos modos explícitos:

```text
[ Escribir ] [ Mapa ]
```

`Escribir` contiene el textarea, la sesión visual y las notas. `Mapa`
contiene los controles de dimensiones, el SVG y el inspector. Las columnas
laterales de revisión y de conocimiento/pendientes permanecen visibles en
ambos modos.

La navegación es un toggle local en JavaScript: no hay rutas nuevas, estado
de conversación ni recarga de página. El modo inicial sigue siendo
`Escribir`.

## Experiencia del mapa

En `Mapa` el área central aprovecha prácticamente la altura disponible de la
ventana. Se mantienen las combinaciones `Characters`, `Lore` y `Plot`, el
filtro de pendientes, `Centrar vista`, tooltips de relaciones y selección de
nodos. El layout SVG continúa siendo determinista y la UI no recalcula ni
duplica la semántica de `GraphProjection`.

El inspector pertenece ahora al mapa. Se abre dentro de la columna central al
seleccionar un nodo, muestra nombre, tipo y las secciones estructuradas que
devuelve `InspectorProjection`, y permite `Ver entorno`/`Ver todo`. Al cerrar
el inspector, el grafo vuelve a ocupar todo el ancho central. No hay edición,
fijación, descarte, resolución ni llamadas AI desde esta vista.

## Estado conservado

El cambio de `Escribir` a `Mapa` y de vuelta sólo alterna visibilidad. No se
recarga el documento ni se reconstruyen los controles de escritura. Por ello
se conservan en la misma página:

- texto aún presente en el textarea;
- conversación visual;
- notas de trabajo en `localStorage`;
- revisión pendiente y sus checkboxes;
- selección/foco del grafo mientras la página sigue viva.

Las sidebars siguen siendo contexto estable: la derecha continúa mostrando
conocimiento establecido/abierto y pendientes abiertos/aceptados; no se
convierte en inspector.

## Layout resultante

```text
┌──────────────┬──────────────────────────────────────┬──────────────┐
│ Revisión     │ [ Escribir ] [ Mapa ]                │ Conocimiento │
│              │                                      │ Pendientes   │
│              │  modo activo                         │              │
└──────────────┴──────────────────────────────────────┴──────────────┘
```

En modo `Escribir`, el centro sigue priorizando escritura, notas e historial.
En modo `Mapa`, el mismo centro se transforma en una superficie de
observación: controles arriba, grafo grande debajo e inspector interno sólo
cuando hace falta.

## Límites deliberadamente intactos

No se modificaron `SharedWorld`, `GraphProjection`, `InspectorProjection`,
los endpoints, CognitiveLoop ni la semántica de las lentes. Tampoco se
añadieron zoom, pan, clustering, scores narrativos, clasificación semántica,
bombilla Socrática o edición desde el grafo. El mapa sigue siendo una
proyección de lectura del mundo, no una fuente de conocimiento.

## Verificación

Ejecutado:

- `cargo fmt -- --check`: correcto;
- `cargo test --offline`: 206 pasados, 11 ignorados, 0 fallos;
- `cargo clippy --all-targets --all-features --offline -- -D warnings`:
  correcto;
- `node --check web/app.js`: correcto.

El servidor continúa configurado para arrancar en `127.0.0.1:5151`.

Archivos modificados:

- `web/index.html`: modos centrales y reubicación del mapa;
- `web/style.css`: navegación, altura y panel interno del inspector;
- `web/app.js`: cambio de modo y apertura/cierre del inspector.

No se modificó Rust ni se cambió ninguna API.

## Evaluación

La reorganización hace que Taberna se entienda como una única mesa de
trabajo con dos formas de mirar la misma historia: **Escribir** para
construirla y **Mapa** para observar sus relaciones. El grafo deja de sentirse
como un informe al pie y pasa a ser una herramienta principal sin desplazar
el conocimiento ni los pendientes del perímetro.
