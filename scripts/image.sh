#!/bin/sh
# lemo-animi image-adapter shim for claymotion (optional).
# Use it with the legacy gen.sh:
#   LEMO_ANIMI_IMAGE_CMD=/path/to/claymotion/scripts/image.sh
# The preferred entry point is: python scripts/claymotion.py image ...
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$HERE/comfy_qwen.py" "$@"
