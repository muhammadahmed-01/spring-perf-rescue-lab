#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8080}"
VUS="${VUS:-100}"
ITERATIONS="${ITERATIONS:-100000}"
MAX_DURATION="${MAX_DURATION:-15m}"

echo "Waiting for ${BASE_URL}/actuator/health ..."
for i in $(seq 1 90); do
  if curl -sf "${BASE_URL}/actuator/health" >/dev/null; then
    break
  fi
  sleep 2
done

echo "Warmup: 500 requests on fixed endpoint ..."
k6 run -e BASE_URL="${BASE_URL}" -e ENDPOINT=/api/orders/fixed -e MODE=warmup \
  -e VUS=25 -e ITERATIONS=500 -e MAX_DURATION=2m load/k6-load.js >/dev/null

mkdir -p load/results

echo
echo "=== Buggy endpoint (${ITERATIONS} requests, ${VUS} VUs) ==="
k6 run \
  -e BASE_URL="${BASE_URL}" \
  -e ENDPOINT=/api/orders/buggy \
  -e MODE=buggy \
  -e VUS="${VUS}" \
  -e ITERATIONS="${ITERATIONS}" \
  -e MAX_DURATION="${MAX_DURATION}" \
  load/k6-load.js

echo
echo "=== Fixed endpoint (${ITERATIONS} requests, ${VUS} VUs) ==="
k6 run \
  -e BASE_URL="${BASE_URL}" \
  -e ENDPOINT=/api/orders/fixed \
  -e MODE=fixed \
  -e VUS="${VUS}" \
  -e ITERATIONS="${ITERATIONS}" \
  -e MAX_DURATION="${MAX_DURATION}" \
  load/k6-load.js

echo
echo "Query counts (single request):"
curl -s "${BASE_URL}/api/orders/stats/buggy"
echo
curl -s "${BASE_URL}/api/orders/stats/fixed"
echo
