#!/usr/bin/env bash
# Check set-up-machine's code on a fresh Linux machine: build the image, run in-container.sh in a
# throwaway container, and remove the container.
#
#   run.sh <repo folder> <output folder>
#
# No credentials go into the container: nothing from the host's home or environment is passed.
# The output folder gets verify's output and the unit tests' result.
set -euo pipefail
repo=$(cd "$1" && pwd)
out=$(mkdir -p "$2" && cd "$2" && pwd)
here=$(cd "$(dirname "$0")" && pwd)
image=set-up-machine-linux
name=set-up-machine-linux-$$

docker build --quiet --tag "$image" "$here" > /dev/null
trap 'docker rm --force "$name" > /dev/null' EXIT
docker run --name "$name" --volume "$repo:/src:ro" --volume "$out:/out" "$image" \
  bash /src/skills/set-up-machine/scripts/tests/linux/in-container.sh
