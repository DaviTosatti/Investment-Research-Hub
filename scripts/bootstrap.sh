#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
for tool in uv node npm docker; do
  command -v "$tool" >/dev/null || { printf 'Instale %s antes de continuar.\n' "$tool" >&2; exit 1; }
done
if [[ ! -f .env ]]; then
  (umask 077; cp .env.example .env)
fi
uv sync --locked
npm ci --prefix apps/web
docker compose up -d --wait db
uv run alembic upgrade head
printf 'Ambiente preparado. Crie o administrador conforme o README.\n'
