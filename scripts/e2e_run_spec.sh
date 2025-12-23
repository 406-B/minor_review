#!/usr/bin/env bash
set -euo pipefail

# 快速运行单个 E2E spec 的脚本
# 用法: ./scripts/e2e_run_spec.sh auth|canteen|community|profile|all

COMPOSE_FILES="-f docker-compose.e2e.yaml"

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 {auth|canteen|community|profile|all}"
  exit 2
fi

NAME="$1"
case "$NAME" in
  auth)
    SPEC="cypress/e2e/auth.cy.js" ;;
  canteen)
    SPEC="cypress/e2e/canteen.cy.js" ;;
  community)
    SPEC="cypress/e2e/community.cy.js" ;;
  profile)
    SPEC="cypress/e2e/profile.cy.js" ;;
  all)
    SPEC="cypress/e2e/**/*.cy.js" ;;
  *)
    echo "Unknown spec: $NAME"
    echo "Usage: $0 {auth|canteen|community|profile|all}"
    exit 2 ;;
esac

echo "Running Cypress spec for: $NAME -> $SPEC"

# Run Cypress inside the cypress container and save output for parsing
sudo docker compose $COMPOSE_FILES run --rm --entrypoint "/bin/sh" cypress -c "npx cypress run --spec '$SPEC' --reporter spec" | tee cypress_output.log
EXIT_CODE=${PIPESTATUS[0]:-0}

echo
echo "========== Test Summary =========="
if [ -f cypress_output.log ]; then
  PASSING=$(grep -oP '✔\s+\K\d+(?=\s+passing)' cypress_output.log | tail -1 || echo "0")
  FAILING=$(grep -oP '\\d+(?=\s+failing)' cypress_output.log | tail -1 || echo "0")
  PENDING=$(grep -oP '\\d+(?=\s+pending)' cypress_output.log | tail -1 || echo "0")

  echo "Tests Passed:  ${PASSING}"
  echo "Tests Failed:  ${FAILING}"
  [ "${PENDING}" != "0" ] && echo "Tests Pending: ${PENDING}"

  if [ "${FAILING}" != "0" ]; then
    echo "\nFailed test excerpts:"
    grep -n "failing)" -n cypress_output.log || true
  fi

  echo "\nArtifacts (in repo):"
  echo "  - ./cypress/videos"
  echo "  - ./cypress/screenshots"
fi

rm -f cypress_output.log

exit $EXIT_CODE
