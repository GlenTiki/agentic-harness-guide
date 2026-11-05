#!/bin/sh
set -eu
here=$(dirname "$0")
out=$(sh "$here/nested_repo_trap.sh")
echo "$out"
echo "$out" | grep -q "last commit: commit in inner" || { echo "FAIL: trap not reproduced"; exit 1; }
echo "$out" | grep -q "last commit: commit in outer" || { echo "FAIL: fix not working"; exit 1; }
echo "pipe status:"
a=$(sh -c 'false | tail -n 1; echo $?'); b=$(sh -c 'false > /dev/null; status=$?; tail -n 1 /dev/null; echo $status')
echo "  pipe: $a  captured: $b"
[ "$a" = 0 ] && [ "$b" = 1 ] || { echo FAIL; exit 1; }
echo ok
