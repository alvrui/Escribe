# Current task

<!-- ChatGPT Web writes the task below this marker. Keep the protocol metadata intact. -->

## STD-001 — Método estándar de trabajo Socia ↔ CLI

**Task ID:** STD-001
**Estado:** PROPOSED
**Origen:** Socia
**Objetivo:** establecer el método mínimo y seguro para coordinar proyectos mediante GitHub.

### Propuesta

Adoptar `coordination/` como interfaz operativa entre Socia y CLI:

- `coordination/CURRENT_TASK.md`: tarea activa escrita por Socia para CLI.
- `coordination/RESULT.md`: resultado escrito por CLI para Socia.
- Ambos documentos deben incluir el mismo `Task ID` y uno de estos estados: `COMPLETED`, `FAILED`, `BLOCKED` o `NEEDS_DECISION`.
- GitHub es el bus de coordinación; el webhook activa CLI y el wakeup notifica a Socia cuando hay resultado.

Responsabilidades:

- **Álvaro:** intención, criterio, decisiones no deducibles y aceptación subjetiva.
- **Socia:** convertir intención en tareas, escribir `CURRENT_TASK`, evaluar `RESULT` y encadenar iteraciones.
- **CLI:** inspección, implementación, diagnóstico, pruebas, documentación e iteración técnica; publicar `RESULT`.

Autonomía permitida: modificar el entorno de desarrollo, compilar, ejecutar pruebas, levantar entornos de prueba, inspeccionar el navegador, corregir errores propios y actualizar documentación.

CLI debe detenerse y emitir `NEEDS_DECISION` ante requisitos ambiguos relevantes, alternativas con consecuencias funcionales, riesgo de pérdida de datos, secretos o permisos, operaciones irreversibles, release/promotion, producción o cambios de alcance.

Estructura mínima recomendada del proyecto: `AGENTS.md`, `README.md`, `STATE.md` cuando aplique, `coordination/CURRENT_TASK.md`, `coordination/RESULT.md`, `docs/` y `scripts/`. No añadir más infraestructura hasta validar este método con trabajo real.

### Entrega solicitada

Revisar esta propuesta desde el lado operativo, señalar incompatibilidades o riesgos concretos y devolver `coordination/RESULT.md` con el mismo `Task ID`. No tocar producción ni servicios.
