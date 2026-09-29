# A fresh Linux machine with every harness set-up-machine covers, installed the official way
# and never logged in. No credentials go in: no auth files, tokens or environment from the host.
FROM node:22-bookworm

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 git curl ca-certificates \
 && apt-get clean

RUN useradd --create-home --shell /bin/bash dev
USER dev
WORKDIR /home/dev
ENV NPM_CONFIG_PREFIX=/home/dev/.npm-global \
    PATH=/home/dev/.local/bin:/home/dev/.opencode/bin:/home/dev/.npm-global/bin:$PATH

# Claude Code, Codex, opencode and the Cursor CLI.
RUN curl -fsSL https://claude.ai/install.sh | bash
RUN npm install --global @openai/codex
RUN curl -fsSL https://opencode.ai/install | bash
RUN curl -fsSL https://cursor.com/install | bash

RUN git config --global user.name dev && git config --global user.email dev@example.com
