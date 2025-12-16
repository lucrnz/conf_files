#! /usr/bin/env bash

# Description: Kills the process(es) listening on a specified port.
# Supports optional flags passed directly to the 'kill' command (e.g., -9 for force kill).
# Works on macOS and Linux (requires 'lsof', which is usually pre-installed).
#
# Usage:
#   ./killport.sh <port> [kill options...]
# Examples:
#   ./killport.sh 3000          # Graceful kill (SIGTERM)
#   ./killport.sh 3000 -9        # Force kill (SIGKILL)
#   ./killport.sh 8080 -SIGINT  # Send SIGINT
#
# If permission is denied, run with sudo: sudo ./killport.sh ...

if [ $# -lt 1 ]; then
    echo "Usage: $0 <port> [kill options...]"
    echo "Example: $0 3000 -9"
    exit 1
fi

PORT="$1"
shift  # Remove the port from arguments

# Collect any remaining arguments as kill options (default: none → SIGTERM)
KILL_OPTS="$@"

# Find PIDs listening on the port (lsof -t outputs only PIDs, one per line)
PIDS=$(lsof -t -i :"$PORT" 2>/dev/null)

if [ -z "$PIDS" ]; then
    echo "No process found listening on port $PORT."
    exit 0
fi

echo "Found process(es) on port $PORT: $PIDS"
echo "Killing with: kill $KILL_OPTS $PIDS"

# Execute the kill command
kill $KILL_OPTS $PIDS

if [ $? -eq 0 ]; then
    echo "Process(es) killed successfully."
else
    echo "Kill failed (permission denied or process already gone)."
    echo "Try with sudo or add -9 for force kill."
    exit 1
fi

