# Current task

<!-- ChatGPT Web writes the task below this marker. Keep the protocol metadata intact. -->

## STD-001 — Método estándar de trabajo de proyectos

**Task ID:** STD-001
**Estado:** PROPOSED
**Origen:** Socia
**Destino:** CLI; revisión posterior por Web
**Repositorio:** `alvrui/Escribe`

### Objetivo

Definir y validar una versión mínima, robusta y segura del método estándar para trabajar proyectos coordinando a Álvaro, Socia, CLI y Web mediante GitHub como fuente de verdad.

### Identidades y responsabilidades

- **Álvaro:** aporta intención, prioridades, criterios de aceptación subjetivos y autorizaciones explícitas.
- **Socia:** diseña y coordina; convierte intención en tareas con Task ID, escribe `coordination/CURRENT_TASK.md`, evalúa resultados y encadena sólo tareas seguras.
- **CLI:** ejecuta en el checkout local: entiende → implementa → prueba → corrige → repite mientras el resultado sea objetivamente verificable; publica el resultado en `coordination/RESULT.md`.
- **Web:** actúa como taller interactivo/local para UX, navegador, debugging, supervisión e intervención; lee GitHub y, si necesita ejecutar comandos, los delega en CLI.

### Fuente de verdad y estructura mínima

GitHub es la fuente de verdad. Los avisos sólo indican que hay estado nuevo y nunca sustituyen la lectura de los archivos versionados.

Cada proyecto debe tener, como mínimo:

```text
AGENTS.md
README.md
STATE.md                 # cuando el proyecto necesite estado operativo explícito
docs/
scripts/
coordination/CURRENT_TASK.md
coordination/RESULT.md
```

Debe existir un `project-stack/AGENTS.md` global y un `AGENTS.md` específico por proyecto. Las instrucciones más cercanas concretan las globales sin ampliar permisos de forma implícita.

`CURRENT_TASK.md` y `RESULT.md` deben contener el mismo **Task ID**. Los estados de resultado permitidos son exactamente: `COMPLETED`, `FAILED`, `BLOCKED` y `NEEDS_DECISION`.

### Contrato de ejecución del CLI

CLI puede inspeccionar, implementar, documentar, ejecutar pruebas, levantar entornos de prueba y corregir sus propios fallos. Repite el ciclo mientras cada paso tenga criterio objetivo de verificación.

CLI debe detenerse y publicar `NEEDS_DECISION` ante ambigüedad relevante, decisiones funcionales, pérdida de datos, secretos/permisos, irreversibilidad, release/promotion/production o cualquier cambio de alcance. Producción, `release/` y `current/` nunca se tocan sin autorización explícita de Álvaro.

### Robustez operativa que CLI debe criticar

La revisión debe proponer la versión mínima robusta, cubriendo explícitamente:

- carreras entre tareas, pushes y workers;
- resultados obsoletos y cómo verificar Task ID, commit base y versión antes de aceptarlos;
- reintentos seguros, deduplicación e idempotencia;
- fallos parciales de push, webhook, worker o wakeup;
- contrato de wakeup estándar:

  `PROJECT_UPDATE_READY repo=alvrui/Escribe task=STD-001`

El wakeup debe ser una señal para que Web lea GitHub, no un transporte de contenido. Web debe revisar el resultado publicado y delegar en CLI cualquier comando necesario.

### Entrega solicitada al CLI

Critica esta propuesta desde el lado operativo, señala incompatibilidades y riesgos concretos, y propone la versión mínima robusta. Ejecuta únicamente verificaciones seguras y devuelve `coordination/RESULT.md` con el mismo Task ID y uno de los estados permitidos. No modifiques producción, `release/`, `current/`, servicios, secretos, configuración del webhook ni `coordination/RESULT.md` durante la ejecución si el worker mantiene esa responsabilidad de publicación.
