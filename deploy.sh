#!/bin/bash
# deploy.sh — one-shot setup for Oracle Cloud Ubuntu 22.04
# Run as: bash deploy.sh
set -e

REPO="https://github.com/ToniJansen/jansen-dev-agent.git"
APP_DIR="$HOME/jansen-dev-agent/jansen_dev_agent"
SERVICE="jansen-bot"

echo "==> Updating system..."
sudo apt-get update -qq
sudo apt-get install -y python3 python3-pip git ffmpeg

echo "==> Cloning repo..."
if [ -d "$HOME/jansen-dev-agent" ]; then
  cd "$HOME/jansen-dev-agent" && git pull
else
  git clone "$REPO" "$HOME/jansen-dev-agent"
fi

echo "==> Installing Python dependencies..."
pip3 install --quiet groq requests python-dotenv "python-telegram-bot>=20.0" pytest playwright plotly kaleido
python3 -m playwright install chromium --with-deps

echo "==> Creating .env..."
if [ ! -f "$APP_DIR/.env" ]; then
  cp "$APP_DIR/.env.example" "$APP_DIR/.env"
  echo ""
  echo "  *** EDIT YOUR .env NOW: nano $APP_DIR/.env ***"
  echo "  Fill in: GROQ_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, GITHUB_TOKEN"
  echo ""
  read -p "Press ENTER when .env is ready..."
fi

echo "==> Installing systemd service for bot_listener..."
sudo tee /etc/systemd/system/${SERVICE}.service > /dev/null <<EOF
[Unit]
Description=Jansen Dev Agent — Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=${APP_DIR}
ExecStart=/usr/bin/python3 ${APP_DIR}/bot_listener.py
Restart=always
RestartSec=10
EnvironmentFile=${APP_DIR}/.env

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE}
sudo systemctl restart ${SERVICE}

echo "==> Setting up cron jobs..."
PYTHON3=$(which python3)
( crontab -l 2>/dev/null | grep -v "jansen_dev_agent"; \
  echo "0 2 * * * cd ${APP_DIR} && ${PYTHON3} overnight_agent.py >> /tmp/jansen_overnight.log 2>&1"; \
  echo "0 7 * * * cd ${APP_DIR} && ${PYTHON3} morning_agent.py >> /tmp/jansen_morning.log 2>&1" \
) | crontab -

echo ""
echo "==> Done!"
echo "  Bot status:  sudo systemctl status ${SERVICE}"
echo "  Bot logs:    sudo journalctl -u ${SERVICE} -f"
echo "  Cron logs:   tail -f /tmp/jansen_overnight.log"
