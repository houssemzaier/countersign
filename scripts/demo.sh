#!/usr/bin/env bash
# A countersign loop in a few seconds, with no model: a scripted maker and a scripted checker.
# The checker sends the first report back with changes, then countersigns the second one.
set -euo pipefail

here="$(cd "$(dirname "$0")/.." && pwd)"
if command -v countersign >/dev/null 2>&1; then
  cs() { countersign "$@"; }
else
  cs() { PYTHONPATH="$here/src" python3 -m countersign "$@"; }
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
export COUNTERSIGN_SESSION="$tmp/session"
export COUNTERSIGN_NOTIFY="cat >> $tmp/owner-pings.txt; echo >> $tmp/owner-pings.txt"

say() { printf '\n\033[1m%s\033[0m\n' "$*"; }
quiet_wait() { cs wait --as "$1" --poll 0.2 | awk 'NR == 1 { sub(/  .*/, ""); print; next } /^---$/ { n++; next } n >= 2 && NF { print "   " $0 }'; }

say "1. The owner creates a session"
cs new --max-rounds 4

checker() {
  echo "checker ready" | cs send --as checker --to maker --type ready >/dev/null
  reports=0
  while out="$(cs wait --as checker --poll 0.2)"; do
    case "$out" in
      *"(report"*)
        reports=$((reports + 1))
        if [ "$reports" -eq 1 ]; then
          printf 'changes: my own oracle run shows C2 red.\n- C2: slugify("a  b") is "a--b", expected "a-b".\n' |
            cs send --as checker --to maker --type review --ticket 1 --verdict changes >/dev/null
        else
          printf 'accepted: my own oracle run shows C1 and C2 green.\n' |
            cs send --as checker --to maker --type review --ticket 1 --verdict accepted >/dev/null
        fi ;;
    esac
  done
}
checker &
checker_pid=$!

say "2. The maker says it is ready, and hears the checker"
echo "maker ready" | cs send --as maker --to checker --type ready
quiet_wait maker

say "3. The maker reports ticket 1, round 1"
printf 'commit a1b2c3d (Refs #1)\n| C1 | PASS |\n| C2 | PASS |\n' | cs send --as maker --to checker --type report --ticket 1
say "   The checker verifies it on evidence, and sends it back"
quiet_wait maker

say "4. The maker fixes what the review lists, and reports again"
printf 'commit e4f5a6b (Refs #1)\n| C1 | PASS |\n| C2 | PASS |\n' | cs send --as maker --to checker --type report --ticket 1
say "   The checker countersigns"
quiet_wait maker

say "5. The owner stops the session; the checker's wait ends with STOP"
cs stop --note "demo over"
wait "$checker_pid" || true

say "The session"
cs status

say "What the owner was pinged about"
cat "$tmp/owner-pings.txt"
