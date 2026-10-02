# Remote machine

What changes when the machine is a remote or headless one, such as a VPS that runs agent sessions while the user is away. The steps in `SKILL.md` stay the same; this file covers what they don't, starting from a fresh server image.

## Before the steps

Go through these in order on a fresh server, since each one relies on the one before it. Check each, and propose what's missing. Most need root, so give the user the commands to run.

1. **Size.** Check the machine has at least 4 GB of RAM, Claude Code's floor, and more if other services share it.
2. **Key access.** Check the user signs in with an SSH key. If they still use the password the provider sent, they run `ssh-copy-id root@<host>` from their own machine, typing that password for the last time.
3. **User.** Work as a dedicated unprivileged user, separate from root and from any other service on the machine. The user creates it (`adduser <user>`, `usermod -aG sudo <user>`), copies their key into its `~/.ssh/authorized_keys`, and sets `~/.ssh` to `700` and the file to `600`, both owned by that user. Then they prove a key login as that user in a new connection before turning root login off in step 5, or one mistake locks everyone out.
4. **A sudo password the user types.** Recommend that the user keeps a password for sudo only, while logins stay key-only, so an agent running as that user can't become root without them. Passwordless sudo (`NOPASSWD`) is more convenient and defeats that; when the user picks it, report it as `gap`.
5. **Keys-only SSH.** Write the settings as a drop-in, `/etc/ssh/sshd_config.d/10-hardening.conf`, rather than editing `sshd_config`:

   ```
   PermitRootLogin no
   PasswordAuthentication no
   KbdInteractiveAuthentication no
   ```

   A provider's own `sshd_config` often allows root and password logins, but it includes `sshd_config.d/` near the top, and sshd keeps the first value it reads for each setting, so the drop-in wins. The user checks the syntax with `sshd -t` before reloading (`systemctl reload ssh`; the unit is `sshd` on some distributions), then confirms the three values sshd now uses with `sshd -T | grep -Ei 'permitrootlogin|passwordauthentication|kbdinteractiveauthentication'`. Keep the current connection open until a new key login as the dedicated user works.
6. **Firewall.** Allow only SSH in, on IPv4 and IPv6: `ufw allow OpenSSH`, then `ufw enable`, in that order so enabling it doesn't cut the connection. Check `ufw status verbose` lists the rule for both, with `IPV6=yes` in `/etc/default/ufw`.
7. **Updates.** On a public-facing machine, check that unattended security upgrades are on; turning them on needs root, so give the user the command.
8. **Swap.** Check `swapon --show`. Without swap, a full RAM kills a process, often an agent mid-task. Propose compressed swap in RAM through `systemd-zram-generator`, in `/etc/systemd/zram-generator.conf`:

   ```ini
   [zram0]
   zram-size = ram / 2
   compression-algorithm = zstd
   swap-priority = 100
   ```

   After `systemctl daemon-reload`, `systemd-zram-setup@zram0` formats the device, but only the generated `dev-zram0.swap` unit switches it on, and it needs `systemctl start dev-zram0.swap` the first time; after a reboot it comes up by itself. Add a swap file on disk at a lower priority, so it takes only what zram can't hold: `fallocate -l <size> /swapfile`, `chmod 600 /swapfile`, `mkswap /swapfile`, `swapon --priority 10 /swapfile`, and the line `/swapfile none swap sw,pri=10 0 0` in `/etc/fstab`.
9. **The docker group.** When Docker is installed, check the dedicated user isn't in the `docker` group (`id -nG`). Membership lets any process the user runs, an agent included, become root without the sudo password. Default to `sudo docker`; when the user wants the group anyway, say so and report it as `gap`.

## Signing in a harness without a browser

The normal sign-in opens a browser, which a headless machine lacks. The user picks one, and sets the value themselves; never print or write the token:

- **Claude Code subscription:** the user runs `claude setup-token` on a machine with a working sign-in, then sets `CLAUDE_CODE_OAUTH_TOKEN` on the remote machine, in the profile the persistent session sources, not only the interactive shell.
- **API billing:** the user sets `ANTHROPIC_API_KEY` the same way.

## Settings that are per machine

- **Never copy `~/.claude/settings.json` or another harness's settings from a different machine.** Hook paths in it point at that machine's files. Run this skill on the remote machine instead.
- **The session host's integration.** After this skill has written the harness settings, install the session host's own integration on the remote machine, which writes its own hooks there (e.g. `herdr integration install claude` and `herdr integration install codex`, plus its skill).
- **Git identity and credentials.** Check `git config --global user.name` and `user.email` are set. The user signs in with `gh auth login` on the remote machine, letting it make this machine's own SSH key and token, as *Separate credentials* below asks.
- **`PATH` in non-interactive shells.** On Debian and Ubuntu, `~/.bashrc` returns early when the shell isn't interactive, so a command sent as `ssh <host> '<command>'` doesn't see what it adds, such as nvm's `node`. Run such a command through a login shell (`bash -lc '<command>'`, which reads `~/.profile` and with it `~/.local/bin`), or give the tool's full path, which nvm's tools need either way.
- **MCP servers** are registered outside any repository, so register each one again. A sign-in that needs a browser either prints a URL to open on any device, or waits on a `localhost:<port>` callback. For the callback, the user reconnects with a port forward and runs the sign-in again:

  ```bash
  ssh -L <port>:localhost:<port> <user>@<host>
  ```

## A headless browser

When agents run browser tests on the machine, the user installs Chromium's system libraries as root with `npx playwright install-deps chromium`, and the dedicated user installs the browser with `npx playwright install chromium`. Then check it launches, from a project that depends on Playwright: `node -e "require('playwright').chromium.launch().then(b => b.close())"`. A missing library shows up only at launch, not at install.

## Keeping sessions alive

Start every agent inside the user's session host (e.g. `herdr`, `tmux`), never directly in the SSH shell. A process in the SSH shell dies when the connection drops; one inside the session host keeps running and can be reattached from any device.

## Containing a misled agent

The global rules still apply on a remote machine and cost nothing; keep them. On top of them, propose these to the user, each as `gap` in the report when it isn't in place:

- **Sandbox on.** Keep Claude Code's built-in sandbox on (`/sandbox`); on Linux it needs `bubblewrap` and `socat` installed.
- **Container.** Run the harness inside a container (Docker, Podman) so an agent can't reach the host's filesystem or other services, with egress limited to the model provider's API, the git host and the MCP servers in use.
- **Separate credentials.** Give each machine its own SSH key and git host token, so one leak has one blast radius.

Done when a key login as the dedicated user works while root and password logins are refused, the steps in `SKILL.md` pass on the remote machine, a session started inside the session host survives a disconnect, and each containment item is in place or reported as a `gap`.
