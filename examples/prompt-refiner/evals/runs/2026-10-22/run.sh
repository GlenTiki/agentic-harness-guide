#!/bin/bash
# usage: run.sh <label> <skillfile> <evalfile> <n>   (run from this folder; replies go to ./<label>/)
label=$1; skill=$(realpath "$2"); ev=$(realpath "$3"); n=$4
here=$(pwd)
id=$(basename "$ev" .md | cut -c1-2)
mkdir -p "$here/$label" "$here/clean"
msg="$(cat "$skill")

Use this as your instructions for this chat.

$(python3 -I "$here/extract.py" "$ev")"
cd "$here/clean"
printf '%s' "$msg" | nice -n 10 claude -p --model claude-sonnet-5-5 --tools "" --setting-sources "" --no-session-persistence > "$here/$label/eval$id-run$n.txt"
echo "$label eval$id run$n exit $?"
