# Current task

<!-- ChatGPT Web writes the task below this marker. Keep the protocol metadata intact. -->

## STD-002 — Método estándar de trabajo documental con GitHub

**Task ID:** STD-002  
**Estado:** PROPOSED  
**Origen:** Coordinadora local  
**Destino:** Web y CLI  
**Repositorio:** `alvrui/Escribe`

### Objetivo

Revisar y validar un método sencillo, reproducible y seguro para coordinar proyectos mediante GitHub, Web, Socia/Desktop y CLI.

### Identidades y flujo

- **Álvaro:** intención, criterio y autorización.
- **Web:** coordinación, análisis, diseño y evaluación; usa GitHub como canal documental principal.
- **Socia/Desktop:** taller local interactivo para UX, navegador, debugging, supervisión e intervención manual.
- **CLI:** ejecución autónoma de código, comandos y pruebas en el checkout local.

El flujo es: Web publica `CURRENT_TASK.md` → el worker detecta el cambio → la coordinadora analiza → CLI ejecuta localmente cuando convenga → la coordinadora revisa → publica `RESULT.md` → envía `PROJECT_UPDATE_READY` o `CODEX_RESULT_READY` → Web relee GitHub.

GitHub es la fuente de verdad. Los wakeups son sólo señales para releer; no transportan contenido, instrucciones ni resultados.

### Comunicación documental

Web debe intentar que sus instrucciones, informes, requerimientos y preguntas ocurran mediante `CURRENT_TASK.md`, `RESULT.md` y documentos de `coordination/`. Las dudas deben marcarse como `NEEDS_DECISION` e incluir contexto, alternativas y la decisión concreta requerida, para que Álvaro sólo intervenga cuando sea necesario. No se abre otro canal Desktop para coordinar salvo necesidad explícita.

### Estructura mínima

```text
AGENTS.md
README.md
STATE.md
docs/
scripts/
coordination/CURRENT_TASK.md
coordination/RESULT.md
```

Debe existir `project-stack/AGENTS.md` como guía global y un `AGENTS.md` específico por proyecto. `CURRENT_TASK.md` y `RESULT.md` comparten siempre el Task ID.

### Estados, autonomía y límites

Los estados válidos son `COMPLETED`, `FAILED`, `BLOCKED` y `NEEDS_DECISION`. CLI puede continuar entender → implementar → probar → corregir → repetir mientras el resultado sea objetivamente verificable. Debe detenerse ante ambigüedad relevante, decisiones funcionales, pérdida de datos, secretos o permisos, irreversibilidad, release/promotion/production o cambio de alcance.

Producción y las rutas/áreas `current` nunca se tocan sin autorización explícita de Álvaro. La coordinación no modifica servicios, secretos ni configuración del webhook salvo tarea autorizada.

### Revisión solicitada a Web

Web debe revisar esta propuesta, señalar correcciones y responder documentalmente en GitHub usando el mismo Task ID o una tarea enlazada. Si necesita ejecución local, debe expresarlo como requerimiento para CLI en `CURRENT_TASK.md`; la coordinadora lo analizará y lo delegará cuando corresponda.

### Resultado esperado

Publicar en `coordination/RESULT.md` la revisión de Web con Task ID `STD-002`, estado `COMPLETED`, `FAILED`, `BLOCKED` o `NEEDS_DECISION`, y cualquier ajuste recomendado.
