# AI Reference Handles v0

## Boundary

Taberna mantiene la identidad persistente en el dominio y sólo presenta
handles temporales al modelo:

```text
Persistent identity
        ↓
AI handle (SO1, A1, I1, E1...)
        ↓
model reasoning
        ↓
AI handle
        ↓
strict resolution
        ↓
Persistent identity
```

Los handles se construyen al compilar cada `AiContextPackage`. Se asignan en
orden determinista por UUID persistente, son únicos dentro del paquete y no se
persisten. El mapa interno conserva la correspondencia entre cada handle y su
`TargetRef` real.

## Operaciones cubiertas

Evaluation, sufficiency e Issue proposals, Sócrates, interpretación de
contribuciones y decisiones autorales reciben instrucciones y ejemplos con
handles. Los intérpretes resuelven esos handles antes de construir
`Evaluation`, `Issue`, `SocraticQuestion`, `UserContribution` o decisiones.

El bootstrap conserva un espacio distinto: `object_1` es una referencia local
a un StoryObject que todavía no existe, mientras que `SO1` identifica un
StoryObject existente en el paquete AI. Ninguno de los dos entra en
`SharedWorld` como identidad; sólo la aplicación gobernada genera el UUID
persistente del nuevo objeto.

## Rechazo estricto

En producción se rechazan UUIDs, referencias tipadas como
`Assertion:<uuid>` y cualquier handle ausente. No hay reparación, truncado ni
adivinación. Así, un UUID mal formado como el observado anteriormente queda
identificado como salida inválida de la frontera AI, en vez de poder llegar al
motor.

Los fixtures históricos de tests que todavía usan referencias tipadas sólo
mantienen compatibilidad bajo compilación de tests; las rutas productivas y
los prompts usan handles.

## Invariantes

- `SharedWorld`, `Context`, `ModuleOutput` y `CognitiveLoop` siguen usando
  referencias persistentes reales.
- Los handles no se serializan en snapshots ni sobreviven a la petición.
- La resolución de un handle desconocido falla.
- La interpretación AI no obtiene autoridad sobre la identidad persistente.
- La semántica narrativa, la autoridad y las validaciones de dominio no
  cambian.

## Verificación

La suite offline pasa con 212 tests y contiene cobertura de asignación
determinista, resolución, ausencia de UUIDs en el contexto renderizado y
compatibilidad del bootstrap existente. La validación real con OpenAI queda
separada de la suite offline y debe ejecutarse con la configuración de la
aplicación.
