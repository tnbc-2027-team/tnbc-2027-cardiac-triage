#!/usr/bin/env bash
# check-boards.sh: run ERC and DRC on every board under hardware/.
# CI runs this on every pull request; run it yourself before asking for review.
# Exit code 1 if any board has an ERC or DRC error.
#
# GitHub runs this automatically on every pull request.
set -uo pipefail

KICAD_CLI="${KICAD_CLI:-kicad-cli}"
cd "$(dirname "$0")/.." || exit 1   # repo root
mkdir -p out/reports

failed=0
for pro in hardware/*/*.kicad_pro; do
  [[ -e "$pro" ]] || { echo "No KiCad projects under hardware/."; exit 0; }
  dir="$(dirname "$pro")"
  board="$(basename "$pro" .kicad_pro)"

  echo "==> $board: ERC"
  if ! "$KICAD_CLI" sch erc --severity-error --exit-code-violations \
       --output "out/reports/$board-erc.rpt" "$dir/$board.kicad_sch"; then
    cat "out/reports/$board-erc.rpt" 2>/dev/null || true
    echo "::error::$board ERC failed"
    failed=1
  fi

  # A board that is still schematic-only has no .kicad_pcb yet: skip DRC.
  if [[ -f "$dir/$board.kicad_pcb" ]]; then
    echo "==> $board: DRC"
    if ! "$KICAD_CLI" pcb drc --schematic-parity --refill-zones --severity-error \
         --exit-code-violations --output "out/reports/$board-drc.rpt" "$dir/$board.kicad_pcb"; then
      cat "out/reports/$board-drc.rpt" 2>/dev/null || true
      echo "::error::$board DRC failed"
      failed=1
    fi
  fi
done

exit "$failed"
