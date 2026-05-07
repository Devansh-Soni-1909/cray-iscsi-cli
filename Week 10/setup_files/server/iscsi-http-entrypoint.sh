#!/bin/bash
set -e

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Trap errors
trap 'log "ERROR: Script failed at line $LINENO"; exit 1' ERR

log "Starting iSCSI Target Metrics HTTP Server"
log "Node: $(hostname)"
log "Target config path: $TARGET_CONFIG_PATH"

# Check if target config path exists
if [ ! -d "$TARGET_CONFIG_PATH" ]; then
    log "WARNING: Target config path $TARGET_CONFIG_PATH does not exist"
    log "This is expected if running on a non-target node"
fi

# Display environment info
log "Python version: $(python3 --version)"
log "Flask version: $(python3 -c 'import flask; print(flask.__version__)' 2>/dev/null || echo 'Flask not installed')"

# Start the HTTP server
log "Starting HTTP server on port 9000..."
exec python3 /app/http_server.py
