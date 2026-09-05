#! /usr/bin/env bash

# Description: Manage local script projects (Python/uv and JS) discovered
# recursively from the current directory (or --dir DIR).
#
# Usage:
#   projects.sh clear [-n] [--dir DIR]   Remove venvs and caches (see below)
#   projects.sh sync [--dir DIR]         Run 'uv sync' on every uv project
#
# clear removes, wherever found under the root:
#   Python: .venv, __pycache__, .pytest_cache, .ruff_cache, .mypy_cache,
#           .coverage, coverage/, htmlcov/
#   JS:     node_modules, .next, .vite, .angular, .turbo, .parcel-cache,
#           .cache, dist/, build/
#   Lockfiles (uv.lock, package-lock.json, bun.lockb, ...) are never touched.
#
# sync only runs on projects containing BOTH pyproject.toml and uv.lock;
# JS-only or non-uv Python projects are reported as skipped (no npm/bun install).
#
# Examples:
#   projects.sh clear -n                # Dry-run: show what would be removed
#   projects.sh clear --dir ~/Development
#   projects.sh sync
#   projects.sh sync --dir=~/Development

set -u

usage() {
    sed -n '3,22p' "$0" | sed 's/^# \{0,1\}//'
    exit 1
}

die() {
    echo "Error: $1" >&2
    exit 1
}

CMD="${1:-}"
[ "$CMD" = "clear" ] || [ "$CMD" = "sync" ] || usage
shift

DRY_RUN=0
ROOT="$PWD"
while [ $# -gt 0 ]; do
    case "$1" in
        -n|--dry-run) DRY_RUN=1 ;;
        --dir)
            [ $# -ge 2 ] || die "--dir requires a value"
            ROOT="$2"
            shift
            ;;
        --dir=*) ROOT="${1#--dir=}" ;;
        *) usage ;;
    esac
    shift
done

[ -d "$ROOT" ] || die "root directory not found: $ROOT"

PROJECTS=$(find "$ROOT" \
    \( -name .git -o -name node_modules -o -name .venv -o -name .cache \
       -o -name __pycache__ -o -name .pytest_cache -o -name .ruff_cache \
       -o -name .mypy_cache -o -name .next -o -name .angular -o -name .turbo \
       -o -name .parcel-cache -o -name dist -o -name build -o -name coverage \
       -o -name htmlcov \) -prune -o \
    -type f \( -name pyproject.toml -o -name package.json \) -printf '%h\n' \
    | sort -u)

if [ -z "$PROJECTS" ]; then
    echo "No script projects found under $ROOT"
    exit 0
fi

echo "Discovered projects under $ROOT:"
echo "$PROJECTS" | sed 's/^/  /'
echo

if [ "$CMD" = "clear" ]; then
    if [ "$DRY_RUN" -eq 1 ]; then
        echo "Dry run: would remove:"
    else
        echo "Removing venvs and caches:"
    fi
    COUNT=0
    ARTIFACTS=$(find "$ROOT" \
        \( -name .git \) -prune -o \
        \( -type d \( -name node_modules -o -name .venv -o -name __pycache__ \
             -o -name .pytest_cache -o -name .ruff_cache -o -name .mypy_cache \
             -o -name coverage -o -name htmlcov -o -name .next -o -name .vite \
             -o -name .angular -o -name .turbo -o -name .parcel-cache \
             -o -name .cache -o -name dist -o -name build \) \
          -o \( -type f -name .coverage \) \) -prune -print | sort)
    if [ -z "$ARTIFACTS" ]; then
        echo "  nothing to remove"
        exit 0
    fi
    while IFS= read -r path; do
        echo "  $path"
        if [ "$DRY_RUN" -eq 0 ]; then
            rm -rf "$path"
        fi
        COUNT=$((COUNT + 1))
    done <<< "$ARTIFACTS"
    if [ "$DRY_RUN" -eq 1 ]; then
        echo "Total: $COUNT item(s) (dry run, nothing deleted)"
    else
        echo "Removed $COUNT item(s)"
    fi
    exit 0
fi

command -v uv >/dev/null 2>&1 || die "'uv' not found in PATH"

PASS=0
FAIL=0
SKIP=0
FAILED=""
SKIPPED=""
while IFS= read -r dir; do
    if [ -f "$dir/pyproject.toml" ] && [ -f "$dir/uv.lock" ]; then
        echo "==> uv sync: $dir"
        if (cd "$dir" && uv sync); then
            PASS=$((PASS + 1))
        else
            FAIL=$((FAIL + 1))
            FAILED="$FAILED\n  $dir"
        fi
    else
        SKIP=$((SKIP + 1))
        SKIPPED="$SKIPPED\n  $dir"
    fi
done <<< "$PROJECTS"

echo
echo "Summary: $PASS synced, $FAIL failed, $SKIP skipped"
[ -n "$SKIPPED" ] && printf 'Skipped (not uv projects):%b\n' "$SKIPPED"
if [ -n "$FAILED" ]; then
    printf 'Failed:%b\n' "$FAILED"
    exit 1
fi
