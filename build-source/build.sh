#!/usr/bin/env bash
# Builds dist/index.html: the password page with the documentation encrypted inside.
# The password is read from the ONBOARDING_PASSWORD environment variable only.
#   ONBOARDING_PASSWORD='...' bash build-source/build.sh
set -euo pipefail

if [ -z "${ONBOARDING_PASSWORD:-}" ]; then
  echo "ONBOARDING_PASSWORD is not set" >&2
  exit 1
fi

here="$(cd "$(dirname "$0")" && pwd)"
root="$(dirname "$here")"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# 1. plain page (with the marker the browser checks after decrypting)
printf '<!--ctv-ok-->' > "$work/plain.html"
python3 -I "$here/build.py" "$work/page.html"
cat "$work/page.html" >> "$work/plain.html"

# 2. encrypt: AES-256-CBC, key and iv from PBKDF2-SHA256 (600000 rounds)
openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -md sha256 -salt \
  -pass env:ONBOARDING_PASSWORD -in "$work/plain.html" -a | tr -d '\n' > "$work/payload.txt"

# 3. put the ciphertext into the password page
mkdir -p "$root/dist"
python3 -I - "$root/index.html" "$work/payload.txt" "$root/dist/index.html" <<'PY'
import sys
template, payload, out = sys.argv[1:4]
html = open(template).read()
assert html.count("__PAYLOAD__") == 1
open(out, "w").write(html.replace("__PAYLOAD__", open(payload).read()))
PY
touch "$root/dist/.nojekyll"
echo "built $root/dist/index.html"
