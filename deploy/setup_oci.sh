#!/usr/bin/env bash
# Instala o Alura Agente em uma instância Ubuntu da OCI.
set -euo pipefail

APP_DIR="/opt/alura-agente"
APP_USER="ubuntu"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Execute com sudo: sudo bash deploy/setup_oci.sh" >&2
  exit 1
fi

if [[ ! -d "${APP_DIR}/.git" ]]; then
  echo "Clone o repositório em ${APP_DIR} antes de executar este script." >&2
  exit 1
fi

if ! id "${APP_USER}" >/dev/null 2>&1; then
  echo "Este instalador espera uma imagem Ubuntu da OCI com o usuário ${APP_USER}." >&2
  exit 1
fi

if [[ ! -s "${APP_DIR}/.env" ]] || ! grep -Eq '^OPENROUTER_API_KEY=.+$' "${APP_DIR}/.env"; then
  echo "Crie ${APP_DIR}/.env e preencha OPENROUTER_API_KEY antes do setup." >&2
  exit 1
fi

apt-get update
apt-get install -y python3-venv python3-pip git curl

chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"
sudo -u "${APP_USER}" -H python3 -m venv "${APP_DIR}/.venv"
sudo -u "${APP_USER}" -H "${APP_DIR}/.venv/bin/python" -m pip install --upgrade pip
sudo -u "${APP_USER}" -H "${APP_DIR}/.venv/bin/python" -m pip install \
  -r "${APP_DIR}/requirements.txt"

cd "${APP_DIR}"
sudo -u "${APP_USER}" -H "${APP_DIR}/.venv/bin/python" scripts/generate_docs.py
sudo -u "${APP_USER}" -H "${APP_DIR}/.venv/bin/python" -m src.ingest

install -m 0644 "${APP_DIR}/deploy/alura-agente.service" \
  /etc/systemd/system/alura-agente.service
systemctl daemon-reload
systemctl enable --now alura-agente.service

if command -v ufw >/dev/null 2>&1 && ufw status | grep -q '^Status: active'; then
  ufw allow 8501/tcp
fi

systemctl --no-pager --full status alura-agente.service
echo "Health check local: curl --fail http://127.0.0.1:8501/_stcore/health"
