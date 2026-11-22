#!/bin/sh
# Install claymotion into the Grok Bot skill library.
# Usage: sh scripts/install_grok.sh [destination]
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DEST=${1:-"$HOME/agent-data/workflows/claymotion"}
mkdir -p "$DEST"
cp -R "$HERE/." "$DEST/"
echo "installed: $DEST"
echo "Grok Bot reads ~/agent-data/workflows/<skill>/; confirm under Settings > Plugins > Yours."
