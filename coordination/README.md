# Protocolo event-driven

Este puente conecta un `push` de GitHub con `codex exec` en un checkout dedicado. Sólo acepta `push` a `main` que incluya `coordination/CURRENT_TASK.md`; ignora el resto. El worker usa `git fetch` + `merge --ff-only`, no sobrescribe cambios locales, serializa ejecuciones con `flock` y publica `coordination/RESULT.md` en un commit posterior.

## Instalación local

Usa un checkout dedicado, separado de producción:

```sh
git clone https://github.com/alvrui/Escribe.git "$HOME/Documents/Codex/escribe"
mkdir -p "$HOME/.config" "$HOME/.local/state/escribe-webhook"
umask 077
secret="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
printf 'GITHUB_WEBHOOK_SECRET=%s\nESCRIBE_REPO=%s\n' "$secret" "$HOME/Documents/Codex/escribe" > "$HOME/.config/escribe-webhook.env"
install -d "$HOME/.config/systemd/user"
install coordination/escribe-webhook.service "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now escribe-webhook.service
```

El `EnvironmentFile` debe ser legible sólo por el usuario del servicio. El receptor escucha en `127.0.0.1:8787` y espera `/github/webhook`; termina TLS en un reverse proxy o túnel autenticado. No expongas el puerto directamente a Internet.

En GitHub, configura un webhook de tipo `application/json`, secreto igual al de ese archivo y evento individual `Just the push event`. Apunta el webhook al endpoint público que reenvíe a `http://127.0.0.1:8787/github/webhook`.

## Pruebas

En una terminal, ejecuta `python3 -m unittest discover -s coordination/tests -v`. Para una prueba manual, cambia el texto bajo el marcador de `CURRENT_TASK.md`, haz commit y push a `main`; comprueba `systemctl --user status escribe-webhook` y `journalctl --user -u escribe-webhook -f`. Un webhook repetido no ejecuta dos workers simultáneamente.

## Retorno

`RESULT.md` es el evento de retorno que ChatGPT Web puede leer. Si está disponible `gh` y se desea una señal adicional, el worker puede evolucionar para crear/actualizar un issue o PR; esta versión no necesita permisos GitHub API adicionales y sólo hace push al remoto configurado. Si el checkout está sucio, el worker no toca sus cambios ni publica un commit: deja el diagnóstico en `~/.local/state/escribe-webhook/last-error.md`.

## Prototipo de wakeup de ChatGPT Web

`coordination/brave_wakeup.py` usa sólo CDP y selectores DOM: localiza una única pestaña abierta de `chatgpt.com`/`chat.openai.com`, rechaza pestañas ambiguas y drafts no vacíos, escribe `CODEX_RESULT_READY` en el compositor y pulsa Enter. No usa coordenadas ni inspecciona cookies, almacenamiento o credenciales.

La integración con el worker es opt-in. Añade `ESCRIBE_WAKEUP=1` al `EnvironmentFile` del servicio y reinícialo; después de publicar correctamente `RESULT.md`, el worker intentará enviar el aviso. Un fallo de CDP no deshace ni invalida el resultado ya publicado.

La instancia actual de Brave no tenía CDP habilitado. No añadas el flag a la instancia ni al perfil que ya usas: Brave suele reutilizar el proceso existente y el flag puede no tener efecto. Arranca una instancia separada con un perfil dedicado:

```sh
mkdir -p "$HOME/.config/BraveSoftware/Brave-Browser-CodexCDP"
/opt/brave.com/brave/brave --remote-debugging-address=127.0.0.1 --remote-debugging-port=9222 --user-data-dir="$HOME/.config/BraveSoftware/Brave-Browser-CodexCDP" https://chatgpt.com/
```

Inicia sesión sólo en ese perfil dedicado y deja abierta una única pestaña de ChatGPT. El perfil actual no se modifica. Si quieres clonar preferencias, cierra Brave completamente primero y haz una copia recuperable del perfil actual antes de copiarlo; nunca copies una base de datos de perfil mientras Brave está abierto. Para volver atrás, cierra la instancia dedicada y elimina sólo `Brave-Browser-CodexCDP`, no `Brave-Browser`.

Comprueba primero sin enviar:

```sh
python3 coordination/brave_wakeup.py --dry-run
```

Cuando el resultado de Codex esté listo, el servicio o un watcher puede ejecutar:

```sh
python3 coordination/brave_wakeup.py
```

El script termina con error si CDP no está disponible, no hay una pestaña ChatGPT, hay más de una, o el compositor contiene un borrador. Esas condiciones evitan enviar el aviso a una pestaña equivocada o destruir texto humano. El mensaje que recibe ChatGPT Web debe instruirle a leer `coordination/RESULT.md` en GitHub.

## Seguridad y límites

El secreto nunca se guarda en Git; la firma se valida con comparación constante, el cuerpo está limitado a 1 MiB y sólo se procesa `main`. El prompt ordena leer `AGENTS.md` si existe. Revisa los cambios antes de instalar o ejecutar el servicio, y mantén este checkout fuera de producción.
