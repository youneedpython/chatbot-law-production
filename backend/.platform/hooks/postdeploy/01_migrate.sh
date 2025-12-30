#!/bin/bash
set -euo pipefail

echo "[postdeploy] migrate start"

## 1. 경로 이동
cd /var/app/current
if [[ -d "backend" ]]; then
  cd backend
fi

pwd
ls -la

## 2. EB가 만든 venv 활성화
VENV_ACTIVATE="$(ls -1d /var/app/venv/*/bin/activate 2>/dev/null | head -n 1 || true)"
if [[ -n "${VENV_ACTIVATE}" ]]; then
  source "${VENV_ACTIVATE}"
  echo "[postdeploy] venv activated: ${VENV_ACTIVATE}"
else
  echo "[postdeploy] WARN: venv activate not found under /var/app/venv/*/bin/activate"
fi

echo "[postdeploy] python=$(which python)"
python -V


## 3. DATABASE_URL 확인 (없으면 배포 실패)
python -c "from app.core.config import DATABASE_URL; import sys; print('[postdeploy] DATABASE_URL=', DATABASE_URL); sys.exit(0 if DATABASE_URL else 1)"


## 4. revision 없으면 upgrade만 skip(배포는 성공)
if ! ls -1 alembic/versions/*.py >/dev/null 2>&1; then
  echo "[postdeploy] WARN: no alembic revisions found. Skip upgrade (initial migration not created yet)."
  exit 0
fi

## 5. revision 있으면 upgrade head
python -m alembic upgrade head
python -m alembic current || echo "[postdeploy] WARN: alembic current failed"
python -m alembic history || echo "[postdeploy] WARN: alembic history failed"

echo "[postdeploy] migrate done"
