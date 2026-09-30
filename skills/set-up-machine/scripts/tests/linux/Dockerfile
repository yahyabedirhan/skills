# A fresh Linux machine with Python and Node (for the skills CLI), and Codex for its rule checker.
# No credentials go in: no auth files, tokens or environment from the host.
FROM node:22-bookworm

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 git ca-certificates \
 && apt-get clean

RUN useradd --create-home --shell /bin/bash dev
USER dev
WORKDIR /home/dev
ENV NPM_CONFIG_PREFIX=/home/dev/.npm-global \
    PATH=/home/dev/.npm-global/bin:$PATH

RUN npm install --global @openai/codex
