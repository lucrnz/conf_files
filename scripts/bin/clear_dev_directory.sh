#!/usr/bin/env bash

TARGET_PATH="$@"
if [ ! -d "$TARGET_PATH" ]; then
    echo "Directory $TARGET_PATH does not exist."
    exit 1
fi

read -r -p "This script will remove directories and its contents permanently - Are you sure? [y/N] " response
case "$response" in
    [yY][eE][sS]|[yY])

        find "$TARGET_PATH" \( \
            -name "dist" -o \
            -name "node_modules" -o \
            -name ".astro" -o \
            -name ".next" -o \
            -name ".nuxt" -o \
            -name "bin" -o \
            -name "obj" -o \
            -name ".angular" -o \
            -name ".svelte-kit" -o \
            -name ".gradle" \
        \) -type d -exec rm -rf {} +
        ;;
    *)
        exit 1;
        ;;
esac
