#!/bin/bash
# Script wrapper para Claude Desktop no Windows com WSL.
# Carrega credenciais do ~/.config/omie-mcp/.env e executa o servidor MCP.
set -e

ENV_FILE="$HOME/.config/omie-mcp/.env"

if [ -f "$ENV_FILE" ]; then
  set -o allexport
  source "$ENV_FILE"
  set +o allexport
fi

exec uvx --from git+https://github.com/lucassampsouza/omie-mcp omie-mcp
