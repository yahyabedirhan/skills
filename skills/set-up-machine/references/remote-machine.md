# Remote machine

What changes when the machine is a remote or headless one, such as a VPS that runs agent sessions while the user is away. The steps in `SKILL.md` stay the same; this file covers what they don't.

Brand-new machine? Set up its base first with [new-remote-machine.md](new-remote-machine.md), then come back here.

## Signing in a harness without a browser

The normal sign-in opens a browser, which a headless machine lacks. The user picks one, and sets the value themselves; never print or write the token:

- **Claude Code subscription:** the user runs `claude setup-token` on a machine with a working sign-in, then sets `CLAUDE_CODE_OAUTH_TOKEN` on the remote machine, in the profile the persistent session sources, not only the interactive shell.
- **API billing:** the user sets `ANTHROPIC_API_KEY` the same way.

## Settings that are per machine

- **Never copy `~/.claude/settings.json` or another harness's settings from a different machine.** Hook paths in it point at that machine's files. Run this skill on the remote machine instead, and rerun any tool integration that writes its own hook there (e.g. a session host's `integration install`).
- **MCP servers** are registered outside any repository, so register each one again. A sign-in that needs a browser either prints a URL to open on any device, or waits on a `localhost:<port>` callback. For the callback, the user reconnects with a port forward and runs the sign-in again:

  ```bash
  ssh -L <port>:localhost:<port> <user>@<host>
  ```

## Keeping sessions alive

Start every agent inside the user's session host (e.g. `herdr`, `tmux`), never directly in the SSH shell. A process in the SSH shell dies when the connection drops; one inside the session host keeps running and can be reattached from any device.

## Containing a misled agent

The global rules still apply on a remote machine and cost nothing; keep them. On top of them, propose these to the user, each as `gap` in the report when it isn't in place:

- **Sandbox on.** Keep Claude Code's built-in sandbox on (`/sandbox`); on Linux it needs `bubblewrap` and `socat` installed.
- **Container.** Run the harness inside a container (Docker, Podman) so an agent can't reach the host's filesystem or other services, with egress limited to the model provider's API, the git host and the MCP servers in use.
- **Separate credentials.** Give each machine its own SSH key and git host token, so one leak has one blast radius.

Done when the steps in `SKILL.md` pass on the remote machine, a session started inside the session host survives a disconnect, and each containment item is in place or reported as a `gap`.
