# New VPS

Setting up a new VPS from a provider's image, so agents can run on it. Go through the base with the user before the steps in `SKILL.md`, then finish with the items after them. Check each item and propose what's missing. Most need root, so give the user the commands to run.

## The base, before the steps

Go in this order, since each item relies on the one before it.

1. **Size.** Check the machine has at least 4 GB of RAM, Claude Code's floor, and more if other services share it.
2. **Key access.** Check the user signs in with an SSH key. If they still use the password the provider sent, they run `ssh-copy-id root@<host>` from their own machine, typing that password for the last time.
3. **User.** Work as a dedicated unprivileged user, separate from root and from any other service on the machine. The user creates it (`adduser <user>`, `usermod -aG sudo <user>`), copies their key into its `~/.ssh/authorized_keys`, and sets `~/.ssh` to `700` and the file to `600`, both owned by that user. Then they prove a key login as that user in a new connection before turning root login off in item 5, or one mistake locks everyone out.
4. **A sudo password the user types.** Recommend that the user keeps a password for sudo only, while logins stay key-only, so an agent running as that user can't become root without them. Passwordless sudo (`NOPASSWD`) is more convenient and defeats that; when the user picks it, report it as `gap`.
5. **Keys-only SSH.** Write the settings as a drop-in, `/etc/ssh/sshd_config.d/10-hardening.conf`, rather than editing `sshd_config`:

   ```
   PermitRootLogin no
   PasswordAuthentication no
   KbdInteractiveAuthentication no
   ```

   A provider's own `sshd_config` often allows root and password logins, but it includes `sshd_config.d/` near the top, and sshd keeps the first value it reads for each setting, so the drop-in wins. The user checks the syntax with `sshd -t` before reloading (`systemctl reload ssh`; the unit is `sshd` on some distributions), then confirms the three values sshd now uses with `sshd -T | grep -Ei 'permitrootlogin|passwordauthentication|kbdinteractiveauthentication'`. Keep the current connection open until a new key login as the dedicated user works.
6. **Firewall.** Allow only SSH in, on IPv4 and IPv6: `ufw allow OpenSSH`, then `ufw enable`, in that order so enabling it doesn't cut the connection. Check `ufw status verbose` lists the rule for both, with `IPV6=yes` in `/etc/default/ufw`.
7. **Updates.** Check that unattended security upgrades are on, since the machine faces the internet.
8. **Swap.** Check `swapon --show`. Without swap, a full RAM kills a process, often an agent mid-task. Propose compressed swap in RAM through `systemd-zram-generator`, in `/etc/systemd/zram-generator.conf`:

   ```ini
   [zram0]
   zram-size = ram / 2
   compression-algorithm = zstd
   swap-priority = 100
   ```

   After `systemctl daemon-reload`, `systemd-zram-setup@zram0` formats the device, but only the generated `dev-zram0.swap` unit switches it on, and it needs `systemctl start dev-zram0.swap` the first time; after a reboot it comes up by itself. Add a swap file on disk at a lower priority, so it takes only what zram can't hold: `fallocate -l <size> /swapfile`, `chmod 600 /swapfile`, `mkswap /swapfile`, `swapon --priority 10 /swapfile`, and the line `/swapfile none swap sw,pri=10 0 0` in `/etc/fstab`.
9. **The docker group.** When Docker is installed, check the dedicated user isn't in the `docker` group (`id -nG`). Membership lets any process the user runs, an agent included, become root without the sudo password. Default to `sudo docker`; when the user wants the group anyway, say so and report it as `gap`.

## After the steps

1. **The session host's integration.** Once the steps in `SKILL.md` have written the harness settings, install the session host's own integration, which writes its own hooks (e.g. `herdr integration install claude` and `herdr integration install codex`, plus its skill).
2. **Git identity and credentials.** Check `git config --global user.name` and `user.email` are set. The user signs in with `gh auth login` on the machine, letting it make this machine's own SSH key and token, as *Separate credentials* in `remote-machine.md` asks.
3. **`PATH` in non-interactive shells.** On Debian and Ubuntu, `~/.bashrc` returns early when the shell isn't interactive, so a command sent as `ssh <host> '<command>'` doesn't see what it adds, such as nvm's `node`. Run such a command through a login shell (`bash -lc '<command>'`, which reads `~/.profile` and with it `~/.local/bin`), or give the tool's full path, which nvm's tools need either way.
4. **A headless browser,** when agents run browser tests on the machine. The user installs Chromium's system libraries as root with `npx playwright install-deps chromium`, and the dedicated user installs the browser with `npx playwright install chromium`. Then check it launches, from a project that depends on Playwright: `node -e "require('playwright').chromium.launch().then(b => b.close())"`. A missing library shows up only at launch, not at install.

Done when a key login as the dedicated user works while root and password logins are refused, swap is on in both places, and each item is in place or reported as a `gap`.
