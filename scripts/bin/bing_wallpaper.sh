#!/usr/bin/env sh

ensure_cmd() {
    which $1 >/dev/null 2>&1 || (echo "$1 not found." && exit 1)
}

ensure_cmd curl && \
ensure_cmd xwallpaper

OUTPUT="$HOME/bing_wallpaper"
API_URL="https://bing.biturl.top/"

curl -fsSL -G "$API_URL" \
    -d "resolution=1920" \
    -d "format=image" \
    -d "mkt=random" \
    -o "$OUTPUT" && \
xwallpaper --zoom "$OUTPUT"
