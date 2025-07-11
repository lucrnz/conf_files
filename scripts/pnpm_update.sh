#!/usr/bin/env bash

# check if jq is installed
if ! command -v jq &> /dev/null
then
    echo "jq is not installed."
    exit 1
fi

LATEST_VESION_URL=$(curl -s https://api.github.com/repos/pnpm/pnpm/releases/latest | jq -r '.assets[] | select(.name == "pnpm-linux-x64") | .browser_download_url')
PNPM_DIR="$HOME/.local/opt/pnpm"

curl -L $LATEST_VESION_URL -o $PNPM_DIR/pnpm && \
chmod +x $PNPM_DIR/pnpm && \
pnpm -v
