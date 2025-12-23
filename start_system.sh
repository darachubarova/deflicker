#!/bin/bash

# Mask Stabilization System - Auto Start
# Usage: ./start_system.sh [--setup-keys|--status|--stop|--logs|--tunnel|--help]

REMOTE_USER="Admin"
REMOTE_HOST="23.189.104.205"
FRONTEND_PORT=8080
BACKEND_PORT=8000
PROJECT_DIR="/tf/darachubarova/defliker"
LOG_DIR="$PROJECT_DIR/logs"
SSH_KEY="$HOME/.ssh/id_tunnel"

print_ok() { echo "[OK] $1"; }
print_err() { echo "[ERR] $1"; }
print_info() { echo "[i] $1"; }

stop_all() {
    print_info "Stopping all processes..."
    pkill -f "uvicorn src.main:app" 2>/dev/null || true
    pkill -f "python3 -m http.server $FRONTEND_PORT" 2>/dev/null || true
    pkill -f "ssh.*-R.*$REMOTE_HOST" 2>/dev/null || true
    sleep 2
    print_ok "All processes stopped"
}

start_backend() {
    print_info "Starting Backend..."
    cd "$PROJECT_DIR"
    mkdir -p "$LOG_DIR"
    nohup uvicorn src.main:app --host 0.0.0.0 --port $BACKEND_PORT > "$LOG_DIR/backend.log" 2>&1 &
    sleep 10
    if curl -s "http://localhost:$BACKEND_PORT" > /dev/null 2>&1; then
        print_ok "Backend started (port $BACKEND_PORT)"
        return 0
    fi
    print_err "Backend failed! Check $LOG_DIR/backend.log"
    return 1
}

start_frontend() {
    print_info "Starting Frontend..."
    cd "$PROJECT_DIR/frontend"
    nohup python3 -m http.server $FRONTEND_PORT > "$LOG_DIR/frontend.log" 2>&1 &
    sleep 2
    if curl -s "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1; then
        print_ok "Frontend started (port $FRONTEND_PORT)"
        return 0
    fi
    print_err "Frontend failed!"
    return 1
}

start_tunnel() {
    print_info "Starting SSH tunnel to $REMOTE_HOST..."
    local ssh_opts="-o StrictHostKeyChecking=no -o ServerAliveInterval=60 -o ServerAliveCountMax=3"
    
    if [ -f "$SSH_KEY" ]; then
        ssh_opts="$ssh_opts -i $SSH_KEY"
        nohup ssh $ssh_opts -N \
            -R 0.0.0.0:$BACKEND_PORT:localhost:$BACKEND_PORT \
            -R 0.0.0.0:$FRONTEND_PORT:localhost:$FRONTEND_PORT \
            ${REMOTE_USER}@${REMOTE_HOST} > "$LOG_DIR/tunnel.log" 2>&1 &
        sleep 10
        print_ok "SSH tunnel created"
    else
        print_err "No SSH key found!"
        print_info "Run: $0 --setup-keys"
        print_info "Or start tunnel manually:"
        echo ""
        echo "ssh -R 0.0.0.0:$BACKEND_PORT:localhost:$BACKEND_PORT -R 0.0.0.0:$FRONTEND_PORT:localhost:$FRONTEND_PORT ${REMOTE_USER}@${REMOTE_HOST}"
        echo ""
    fi
}

setup_keys() {
    echo "============================================="
    echo "     SSH Keys Setup"
    echo "============================================="
    
    mkdir -p ~/.ssh
    if [ ! -f "$SSH_KEY" ]; then
        ssh-keygen -t ed25519 -f "$SSH_KEY" -N "" -C "mask-tunnel"
        chmod 600 "$SSH_KEY"
        print_ok "Key created: $SSH_KEY"
    else
        print_info "Key already exists: $SSH_KEY"
    fi
    
    echo ""
    echo "============================================="
    echo "Run this on Windows (PowerShell as Admin):"
    echo "============================================="
    echo ""
    echo "Add-Content -Path \"C:\ProgramData\ssh\administrators_authorized_keys\" -Value '$(cat $SSH_KEY.pub)'"
    echo ""
    echo "icacls \"C:\ProgramData\ssh\administrators_authorized_keys\" /inheritance:r /grant \"SYSTEM:(F)\" /grant \"Administrators:(F)\""
    echo ""
    echo "============================================="
    
    read -p "Press Enter after running commands on Windows..." dummy
    
    print_info "Testing connection..."
    if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -i "$SSH_KEY" ${REMOTE_USER}@${REMOTE_HOST} "echo OK" 2>/dev/null | grep -q "OK"; then
        print_ok "SSH key works! You can now run: $0"
    else
        print_err "Connection failed. Check Windows settings."
    fi
}

start_system() {
    echo "============================================="
    echo "     Mask Stabilization System"
    echo "============================================="
    
    stop_all
    echo ""
    start_backend || exit 1
    start_frontend || exit 1
    
    print_info "Updating Frontend config..."
    sed -i "s|const API_BASE = '.*';|const API_BASE = 'http://$REMOTE_HOST:$BACKEND_PORT';|" "$PROJECT_DIR/frontend/index.html"
    print_ok "API_BASE set to http://$REMOTE_HOST:$BACKEND_PORT"
    
    start_tunnel
    
    echo ""
    echo "============================================="
    echo "  System started!"
    echo "============================================="
    echo ""
    echo "  Frontend: http://$REMOTE_HOST:$FRONTEND_PORT"
    echo "  Backend:  http://$REMOTE_HOST:$BACKEND_PORT"
    echo "  Logs:     $LOG_DIR/"
    echo "  Stop:     $0 --stop"
    echo ""
}

show_status() {
    echo "=== System Status ==="
    pgrep -f "uvicorn src.main:app" > /dev/null && print_ok "Backend: running" || print_err "Backend: stopped"
    pgrep -f "http.server $FRONTEND_PORT" > /dev/null && print_ok "Frontend: running" || print_err "Frontend: stopped"
    pgrep -f "ssh.*-R.*$REMOTE_HOST" > /dev/null && print_ok "Tunnel: running" || print_err "Tunnel: stopped"
    echo ""
    echo "URLs:"
    echo "  http://$REMOTE_HOST:$FRONTEND_PORT"
    echo "  http://$REMOTE_HOST:$BACKEND_PORT"
}

show_logs() {
    echo "=== Backend (last 20 lines) ==="
    tail -20 "$LOG_DIR/backend.log" 2>/dev/null || echo "No logs"
    echo ""
    echo "=== Frontend ==="
    tail -10 "$LOG_DIR/frontend.log" 2>/dev/null || echo "No logs"
    echo ""
    echo "=== Tunnel ==="
    tail -10 "$LOG_DIR/tunnel.log" 2>/dev/null || echo "No logs"
}

tunnel_interactive() {
    print_info "Starting interactive tunnel (Ctrl+C to exit)..."
    local ssh_opts="-o StrictHostKeyChecking=no -o ServerAliveInterval=60"
    [ -f "$SSH_KEY" ] && ssh_opts="$ssh_opts -i $SSH_KEY"
    ssh $ssh_opts \
        -R 0.0.0.0:$BACKEND_PORT:localhost:$BACKEND_PORT \
        -R 0.0.0.0:$FRONTEND_PORT:localhost:$FRONTEND_PORT \
        ${REMOTE_USER}@${REMOTE_HOST}
}

case "${1:-}" in
    --setup-keys|-k) setup_keys ;;
    --status|-s) show_status ;;
    --stop|-x) stop_all ;;
    --logs|-l) show_logs ;;
    --tunnel|-t) tunnel_interactive ;;
    --help|-h)
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  (none)        Start the system"
        echo "  --setup-keys  Setup SSH keys for passwordless login"
        echo "  --status      Show system status"
        echo "  --stop        Stop all processes"
        echo "  --logs        Show logs"
        echo "  --tunnel      Start tunnel interactively"
        echo "  --help        Show this help"
        ;;
    *) start_system ;;
esac
