#!/bin/bash
# usage: run.sh <evalfile> <fixture folder> [output folder name, default replies]   (run from this folder)
ev=$(realpath "$1"); fx=$(realpath "$2")
here=$(pwd)
id=$(basename "$ev" .md | cut -c1-2)
out="$here/${3:-replies}"
mkdir -p "$out"
msg="$(python3 -I "$here/extract.py" "$ev")"
skill="$(cat "$fx/my-insights/SKILL.md")
The skill folder is my-insights/ in the current folder."
cd "$fx"
snapshot() { find . -path ./.git -prune -o -type f -print | sort | xargs shasum -a 256; }
before=$(snapshot)
printf '%s' "$msg" | nice -n 10 claude -p --model claude-sonnet-5-5 \
  --append-system-prompt "$skill" \
  --tools "Read,Glob,Grep,Bash,Write" \
  --allowedTools "Read" "Glob" "Grep" "Bash(python3 *insights.py*)" "Write(report/**)" \
  --setting-sources "" --no-session-persistence \
  --output-format stream-json --verbose > "$out/eval$id-transcript.jsonl"
status=$?
after=$(snapshot)
python3 -I "$here/final-text.py" "$out/eval$id-transcript.jsonl" > "$out/eval$id-reply.txt"
{
  echo "exit: $status"
  echo "file changes after the run, compared with before (lines starting > are new or changed):"
  diff <(echo "$before") <(echo "$after") || true
} > "$out/eval$id-changes.txt"
if [ -f report/insights.md ]; then cp report/insights.md "$out/eval$id-report.md"; fi
for f in "$out"/eval$id-*; do
  FX="$fx" python3 -I -c 'import os,sys; p=sys.argv[1]; t=open(p).read(); t=t.replace(os.environ["FX"],"<fixture>").replace(os.path.expanduser("~"),"<home>"); open(p,"w").write(t)' "$f"
done
python3 -I "$here/sanitize.py" "$out/eval$id-transcript.jsonl"
echo "eval$id exit $status"
