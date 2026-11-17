#!/bin/bash
# usage: run.sh <label> <evalfile> <skillfile> <fixture folder>   (run from this folder; output goes to ./<label>/)
label=$1; ev=$(realpath "$2"); skill=$(realpath "$3"); fx=$(realpath "$4")
here=$(pwd)
id=$(basename "$ev" .md | cut -c1-2)
out="$here/$label"
mkdir -p "$out"
msg="$(python3 -I "$here/extract.py" "$ev")"
before=$(cd "$fx" && git status --porcelain --untracked-files=all | sort)
cd "$fx"
printf '%s' "$msg" | nice -n 10 claude -p --model claude-sonnet-5-5 \
  --append-system-prompt "$(cat "$skill")" \
  --tools "Read,Glob,Grep,Bash,Write" \
  --allowedTools "Read" "Glob" "Grep" "Bash(git status:*)" "Bash(git log:*)" "Bash(git worktree list:*)" "Write(goals/**)" "Edit(goals/**)" \
  --setting-sources "" --no-session-persistence \
  --output-format stream-json --verbose > "$out/eval$id-transcript.jsonl"
status=$?
after=$(git status --porcelain --untracked-files=all | sort)
python3 -I "$here/final-text.py" "$out/eval$id-transcript.jsonl" > "$out/eval$id-reply.txt"
{
  echo "exit: $status"
  echo "changes after the run, compared with before (lines starting > are new):"
  diff <(echo "$before") <(echo "$after") || true
} > "$out/eval$id-changes.txt"
if [ -d goals ]; then mkdir -p "$out/eval$id-goals"; cp -R goals/. "$out/eval$id-goals/"; fi
for f in "$out"/eval$id-*.txt "$out"/eval$id-*.jsonl $(find "$out/eval$id-goals" -type f 2>/dev/null); do
  FX="$fx" python3 -I -c 'import os,sys; p=sys.argv[1]; t=open(p).read(); t=t.replace(os.environ["FX"],"<fixture>").replace(os.path.expanduser("~"),"<home>"); open(p,"w").write(t)' "$f"
done
echo "$label eval$id exit $status"
