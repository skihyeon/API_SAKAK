#!/bin/bash

set -e

echo "데이터베이스 마이그레이션을 실행합니다..."
alembic upgrade head
echo "데이터베이스 마이그레이션 완료."

exec "$@"