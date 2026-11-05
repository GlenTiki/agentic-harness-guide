#!/bin/sh
set -eu
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE
root=$(mktemp -d)
trap 'rm -rf "$root"' EXIT
export GIT_CONFIG_GLOBAL=/dev/null GIT_AUTHOR_NAME=a GIT_AUTHOR_EMAIL=a@example.com GIT_COMMITTER_NAME=a GIT_COMMITTER_EMAIL=a@example.com
for name in outer inner; do
    git init -q -b main "$root/$name"
    echo "$name" > "$root/$name/f"
    git -C "$root/$name" add f
    git -C "$root/$name" commit -q -m "commit in $name"
done
echo "-- GIT_DIR names outer's metadata, git -C inner --"
echo "last commit: $(GIT_DIR="$root/outer/.git" git -C "$root/inner" log -1 --format=%s)"
echo "-- GIT_WORK_TREE names inner's folder, git -C outer --"
echo "git dir: $(GIT_WORK_TREE="$root/inner" git -C "$root/outer" rev-parse --git-dir)"
echo "status: $(GIT_WORK_TREE="$root/inner" git -C "$root/outer" status --short)"
echo "-- GIT_INDEX_FILE names an empty index, git -C outer --"
GIT_INDEX_FILE="$root/empty-index" git -C "$root/outer" status --short
