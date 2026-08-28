# Current task

<!-- ChatGPT Web writes the task below this marker. Keep the protocol metadata intact. -->

## BRIDGE-001 — Prueba segura del puente ChatGPT ↔ Brave

**Task ID:** BRIDGE-001
**Estado:** PROPOSED
**Origen:** Web
**Destino:** CLI; coordinación y evaluación por Web
**Repositorio:** `alvrui/Escribe`

### Objetivo

Diagnosticar y probar de forma segura el puente bidireccional ChatGPT Desktop ↔ Brave implementado en `coordination/brave_wakeup.py`.

### Trabajo solicitado

1. Inspeccionar los prerrequisitos disponibles para portapapeles y automatización de ventana.
2. Ejecutar las comprobaciones de sintaxis y protocolo existentes.
3. Probar Web → portapapeles → Desktop y portapapeles → Web usando únicamente este payload explícito y no sensible:

   `BRIDGE_TEST_BRAVE_DESKTOP_001`

4. Verificar que se mantienen las protecciones contra pestañas múltiples, borradores activos y ventanas Desktop ambiguas.
5. Si falta una dependencia, buscar primero una alternativa ya disponible o instalable en espacio de usuario. No instalar paquetes del sistema, pedir permisos, enviar contenido real del portapapeles ni modificar servicios.
6. Si la prueba requiere una instalación privilegiada, una decisión de UX o una intervención manual de Álvaro, detenerse y publicar `NEEDS_DECISION` explicando exactamente qué falta.

### Resultado esperado

Publicar `coordination/RESULT.md` con el mismo Task ID `BRIDGE-001`, estado `COMPLETED`, `FAILED`, `BLOCKED` o `NEEDS_DECISION`, comandos/verificaciones realizados, resultado de cada dirección del puente y cualquier limitación concreta.
