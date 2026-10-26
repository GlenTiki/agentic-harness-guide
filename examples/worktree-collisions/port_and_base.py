#!/usr/bin/env python3
"""Two processes in two folders bind one port. Then check whether a branch descends from the current base."""
import pathlib
import socket
import subprocess
import sys
import tempfile

from shared_checkout import git, new_repo

BIND = (
    "import errno, socket, sys\n"
    "s = socket.socket()\n"
    "try:\n"
    "    s.bind(('127.0.0.1', int(sys.argv[1])))\n"
    "except OSError as e:\n"
    "    print(sys.argv[2], 'failed:', errno.errorcode[e.errno], flush=True)\n"
    "else:\n"
    "    print(sys.argv[2], 'bound', flush=True)\n"
    "    sys.stdin.readline()\n"
)


def free_port():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def start(folder, port, label):
    return subprocess.Popen(
        [sys.executable, "-I", "-c", BIND, str(port), label],
        cwd=folder, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
    )


def port_collision(root):
    folders = [root / "folder-a", root / "folder-b"]
    for folder in folders:
        folder.mkdir()
    print("-- two folders, one port --")
    port = free_port()
    first = start(folders[0], port, "process in folder-a")
    print(first.stdout.readline().strip())
    second = start(folders[1], port, "process in folder-b")
    print(second.stdout.readline().strip())
    second.wait()
    print("-- one port per folder, taken from the folder's position in the list --")
    base = free_port()
    ports = [base + index for index, _ in enumerate(folders)]
    other = [start(folder, number, f"process in {folder.name}") for folder, number in zip(folders, ports)]
    print("\n".join(p.stdout.readline().strip() for p in other))
    for process in [first, *other]:
        process.communicate("\n")


def descends_from_base(root):
    repo = new_repo(root, "based")
    tree = root / "based-tree"
    git(repo, "worktree", "add", "-q", "-b", "agent/late", str(tree), "main")
    (repo / "notes.txt").write_text("title: moved on\n")
    git(repo, "commit", "-q", "-am", "main moves on")
    check = git(repo, "merge-base", "--is-ancestor", "main", "agent/late", check=False)
    print("-- main moved after the worktree was made --")
    print("branch descends from current main, exit code:", check.returncode)
    git(tree, "rebase", "-q", "main")
    print("after rebasing the branch onto main, exit code:",
          git(repo, "merge-base", "--is-ancestor", "main", "agent/late", check=False).returncode)


def nested_ignored_repository(root):
    repo = new_repo(root, "outer")
    (repo / ".gitignore").write_text("inner/\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "ignore the inner repository")
    (repo / "inner").mkdir()
    git(repo / "inner", "init", "-q")
    tree = root / "outer-tree"
    git(repo, "worktree", "add", "-q", "-b", "agent/outer", str(tree), "main")
    print("-- a nested repository that the outer repository ignores --")
    print("inner exists in the main checkout:", (repo / "inner").is_dir())
    print("inner exists in the worktree:", (tree / "inner").is_dir())


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp).resolve()
        port_collision(root)
        descends_from_base(root)
        nested_ignored_repository(root)


if __name__ == "__main__":
    main()
