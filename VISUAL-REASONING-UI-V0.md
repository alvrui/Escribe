# Visual Reasoning UI v0

## Resultado

Taberna ya integra las proyecciones deterministas existentes en la interfaz
web. El autor puede elegir dos lentes (`Characters`, `Lore`, `Plot`), ver un
grafo SVG de los nodos y relaciones actuales, y seleccionar un nodo para
abrir su `InspectorProjection`. El grafo y el inspector son de solo lectura:
no llaman a IA, no modifican `SharedWorld` y no crean una segunda fuente de
verdad.

## Layout

Se conserva el workspace de tres columnas: revisión a la izquierda,
escritura y notas en el centro, y conocimiento/pendientes a la derecha. Bajo
ese workspace aparece **Mapa de la historia**, ocupando todo el ancho. Tiene
selectores de dimensiones, control de pendientes y botón para centrar la
vista. Los nodos se distribuyen de forma estable en SVG; el tamaño refleja
moderadamente `connection_count`, el indicador de pendiente usa
`issue_count` y el grosor de las aristas usa `evidence_count`. Ninguna de
esas señales se presenta como importancia, calidad o drama.

El clic en un nodo solicita el inspector contextual. `Ver entorno` vuelve a
pedir el grafo con `focus` y `Ver todo` elimina el foco. El clic en el fondo
deselecciona. Un mundo vacío muestra “El mapa aparecerá a medida que la
historia crezca”; un solo nodo y nodos desconectados siguen siendo válidos.

## API

```text
POST /api/graph
POST /api/inspect
```

El primer endpoint recibe `GraphProjectionRequest` y devuelve directamente
`GraphProjection`; el segundo recibe `InspectorProjectionRequest` y devuelve
`InspectorProjection`. Los handlers sólo deserializan, delegan en
`from_world` y serializan. Los focos inexistentes se rechazan con HTTP 400.

## Resultado de Paco

La fixture determinista existente sigue verificando Paco, Jefe, Proyecto y
Cliente, con relaciones explicables por Assertions y Issues asociados.
`Characters × Lore`, `Characters × Plot` y `Characters × Characters` son
combinaciones válidas; las dos primeras cambian la selección cuando la
provenance explícita lo permite. Las pruebas también confirman nodos únicos,
evidencia válida, orden determinista, preservación de `Open`/`Fixed`,
exclusión de conocimiento descartado o temporalmente inválido y ausencia de
mutación del mundo.

El inspector expone sólo las secciones que devuelve la proyección, como
“Qué sabemos”, “Relaciones”, “Qué la alimenta”, “Qué conecta” y cuestiones
pendientes. Cada elemento conserva sus `supporting_refs` sin mostrar UUIDs en
la vista normal.

## Limitaciones reales

- `Lore` y `Plot` sólo se distinguen cuando existe provenance explícita; la
  UI no añade inferencia semántica.
- Las posiciones se recalculan y no se persisten.
- No hay zoom, pan, clustering ni optimización para cientos de nodos.
- Sólo se derivan relaciones de Assertions con dos o más StoryObjects.
- El grafo no permite editar, fijar ni resolver conocimiento.
- No se añadió todavía la acción Socrática/bombilla.
- Las notas continúan siendo memoria local del usuario, separada del grafo y
  de `SharedWorld`.

## Presión arquitectónica y evaluación

La integración no necesitó cambiar `SharedWorld`, `GraphProjection` ni
`InspectorProjection`, ni introducir un modelo web paralelo. La presión que
queda visible es la clasificación conservadora basada en provenance: algunas
combinaciones pueden resultar pobres si la historia no declara una
pertenencia explícita a módulo. Se deja como observación para una iteración
posterior, sin compensarla con reglas nuevas.

La proyección es suficientemente coherente para pasar a visualización web:
permite elegir lentes, seguir conexiones explicables, detectar nodos aislados
y pendientes, e inspeccionar un elemento sin mutar el mundo. El siguiente gap
real es comprobar con historias de uso si la separación conservadora de
`Lore × Plot` omite conexiones que el autor espera ver.

## Verificación

- `cargo fmt -- --check`: correcto.
- `cargo test --offline`: 206 pasados, 11 ignorados, 0 fallos.
- `cargo clippy --all-targets --all-features --offline -- -D warnings`:
  correcto.
- `node --check web/app.js`: correcto.
- `cargo run --bin taberna-web`: arranque confirmado en
  `http://127.0.0.1:5151`.

Archivos modificados en Taberna: `src/web.rs`, `web/index.html`,
`web/app.js` y `web/style.css`. No se persistieron proyecciones ni
coordenadas visuales.
