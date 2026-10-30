#!/usr/bin/env bash
set -euo pipefail
cd /tmp/aegis-term/repo
while [[ ! -f /tmp/range-env-c-1.json.receipt.json || ! -f /tmp/range-env-c-2.json.receipt.json ]]; do
  sleep 30
done
export NODE_PATH=/workspace/aegis-performance-f/docs/performance/F/node_modules
exec taskset -c 0-3 python docs/missile/range/A/postprocess.py /tmp/range-env-c-1.json /tmp/range-env-c-2.json
