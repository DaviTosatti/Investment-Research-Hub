#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
uv run python scripts/sync_agent_skills.py --check
uv run ruff check apps/api packages/engines tests
uv run mypy
uv run pytest -q
uv run alembic check
npm --prefix apps/web run test
npm --prefix apps/web run typecheck
npm --prefix apps/web run lint
NEXT_TELEMETRY_DISABLED=1 npm --prefix apps/web run build
