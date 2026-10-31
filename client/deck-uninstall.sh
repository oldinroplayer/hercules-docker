#!/usr/bin/env bash
# Removes Family RO from the Steam Deck (see deck-install.sh). In Desktop Mode, with Steam
# closed, open Konsole and run:
#
#   curl -fsSL https://raw.githubusercontent.com/NumbaWon/hercules-docker/main/client/deck-uninstall.sh | bash
#
# Options go after "bash -s --", e.g.  ... | bash -s -- --keep-files
# Run from a checkout it uses the files beside it instead of downloading them.
set -euo pipefail

RAW=https://raw.githubusercontent.com/NumbaWon/hercules-docker/main/client
FILES="install-steamdeck.py uninstall-steamdeck.py ragexe-2020-02-19.patch ragexe-2020-02-19-bigfont.patch CDClient.dll DATA.INI clientinfo.xml"

here=
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
    here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
fi
if [ -z "$here" ] || [ ! -f "$here/install-steamdeck.py" ]; then
    here=$(mktemp -d)
    trap 'rm -rf "$here"' EXIT
    for f in $FILES; do
        curl -fsSL -o "$here/$f" "$RAW/$f"
    done
fi
python3 "$here/uninstall-steamdeck.py" "$@"
