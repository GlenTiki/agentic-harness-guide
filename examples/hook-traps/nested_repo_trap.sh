#!/bin/sh
# Builds two throwaway repositories and shows a hook reading the wrong one when GIT_DIR is inherited.
set -eu
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
for name in outer inner; do
  git init -q "$tmp/$name"
  git -C "$tmp/$name" -c user.name=t -c user.email=t@example.invalid commit -q --allow-empty -m "commit in $name"
done
echo "hook asks about outer, environment points at inner:"
GIT_DIR="$tmp/inner/.git" git -C "$tmp/outer" log -1 --format='  last commit: %s'
echo "same call with the git variables removed:"
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE git -C "$tmp/outer" log -1 --format='  last commit: %s'
