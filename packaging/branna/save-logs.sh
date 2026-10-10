#!/usr/bin/env bash
# Save a Branna workflow job's logs to the `ci-logs-<job>` branch, so they can be read with plain
# git (git fetch origin ci-logs-test) by people and agents without GitHub Actions access.
#
# Usage: packaging/branna/save-logs.sh JOB
# Needs LOGS (the job's log directory), JOB_STATUS, GITHUB_TOKEN and the GitHub Actions variables.
set -euo pipefail

JOB="${1:?usage: save-logs.sh JOB}"
: "${LOGS:?}" "${JOB_STATUS:?}"
mkdir -p "$LOGS"
{
  echo "job: $JOB"
  echo "status: $JOB_STATUS"
  echo "branch: ${GITHUB_REF_NAME:-}"
  echo "commit: ${GITHUB_SHA:-}"
  echo "run: ${GITHUB_SERVER_URL:-}/${GITHUB_REPOSITORY:-}/actions/runs/${GITHUB_RUN_ID:-}"
  echo "finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$LOGS/summary.txt"
# Keep the end of each log: that is where errors and test results are.
for f in "$LOGS"/*.log; do
  [ -f "$f" ] || continue
  tail -n 6000 "$f" > "$f.tail" && mv "$f.tail" "$f"
done
"$(dirname "${BASH_SOURCE[0]}")/publish.sh" "$LOGS" "ci-logs-$JOB" "Logs: $JOB ($JOB_STATUS) for ${GITHUB_REF_NAME:-}"
