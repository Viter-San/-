#!/bin/bash
set -e

SERVICE_DIR="/opt/morph-execd"
SERVICE_FILE="/etc/systemd/system/morph-execd.service"
PYTHON_EXE="$(which python3)"

# 1. Створюємо структуру директорій
mkdir -p "$SERVICE_DIR/logs"

# 2. Копіюємо скрипт агента
cp morph_execd.py "$SERVICE_DIR/morph_execd.py"
chmod 700 "$SERVICE_DIR/morph_execd.py"

# 3. Встановлюємо Flask, якщо потрібно
pip3 install --quiet flask

# 4. Створюємо systemd юніт
cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=Morph Execution Daemon
After=network.target

[Service]
ExecStart=$PYTHON_EXE $SERVICE_DIR/morph_execd.py
WorkingDirectory=$SERVICE_DIR
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

# 5. Перезапуск systemd, запуск служби
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable morph-execd
systemctl restart morph-execd

# 6. Перевірка
systemctl status morph-execd --no-pager
