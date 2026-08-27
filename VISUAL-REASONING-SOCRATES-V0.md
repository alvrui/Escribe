# Visual Reasoning → Sócrates v0

## Flujo

El Mapa permite seleccionar un `Issue` visible y pedir una exploración
contextual. La ruta es:

```text
Issue seleccionado
    ↓
POST /api/explore-issue
    ↓
validación del Issue + Context Compiler
    ↓
Socrates
    ↓
una SocraticQuestion
    ↓
modo Escribir
```

La operación es de sólo lectura. No crea Assertions, no cambia el estado del
Issue, no ejecuta GovernedInteraction y no altera `SharedWorld`. Un Issue
`Accepted` puede explorarse; un Issue `Resolved` se rechaza.

## Contexto y autoridad

Sócrates recibe el Issue real seleccionado junto con un `ContextResponse`
ensamblado a partir de los StoryObjects asociados al Issue. También recibe el
objetivo de exploración, las Assertions, evaluaciones, reacciones y estados
que el compilador de contexto haga visibles.

La interfaz no expone `SharedWorld` directamente y no añade conocimiento
especial de Issues al contrato de Sócrates. La pregunta devuelta es una
propuesta para continuar pensando: no resuelve el Issue ni fija canon.

## Interfaz

En el inspector de un Issue aparece `💡 Explorar`. Al recibir la pregunta,
Taberna cambia a `Escribir` y la muestra en una tarjeta de Sócrates encima del
textarea. El textarea queda vacío para que la respuesta del usuario continúe
por el flujo normal de interpretación, revisión y aplicación.

La pregunta se muestra directamente porque ya es lenguaje humano; no se hace
una segunda llamada al Presenter. La acción no se ofrece todavía para nodos
de StoryObject ni para aristas.

## Fixture Paco

La prueba offline usa un Issue abierto sobre Paco y un StoryObject asociado.
El fake de Sócrates confirma que recibe el Issue correcto y un contexto que
contiene el personaje. También se verifica que el mismo flujo permite Issues
`Accepted`, rechaza Issues inexistentes o `Resolved`, propaga un fallo de
Sócrates y mantiene el mundo intacto en todos los casos.

La validación manual con la historia Paco/Laura queda pendiente de ejecutarse
con una instancia configurada con API key. La pregunta debe evaluarse por su
fidelidad al contexto, su utilidad para desarrollar el pendiente y la ausencia
de hechos inventados, no por estilo literario.

## ¿Hace accionable el grafo?

**PARTIALLY.** La acción convierte un Issue seleccionado en un siguiente paso
usable y conserva la autoridad del autor. Aún no hay exploración desde nodos o
aristas, memoria conversacional ni una evaluación de la calidad narrativa de
la pregunta.

## NEXT REAL GAP

Validar con una historia real que las preguntas contextualizadas son
consistentemente fértiles sin repetir el texto del Issue.
