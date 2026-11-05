#!/usr/bin/env python3
"""Two processes in two folders bind one port. Then check whether a branch descends from the current base."""
import pathlib
import select
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
    "    print(sys.argv[2], 'bound', s.getsockname()[1], flush=True)\n"
    "    sys.stdin.readline()\n"
)
WAIT_SECONDS = 10


def start(folder, port, label):
    return subprocess.Popen(
        [sys.executable, "-I", "-c", BIND, str(port), label],
        cwd=folder, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
    )


def read_line(process, seconds=WAIT_SECONDS):
    ready, _, _ = select.select([process.stdout], [], [], seconds)
    if not ready:
        raise TimeoutError(f"no output within {seconds} seconds")
    return process.stdout.readline().strip()


def stop(processes):
    for process in processes:
        process.kill()
        process.communicate()


def bound_port(line):
    return int(line.rsplit(" ", 1)[1])


def port_collision(root):
    folders = [root / "folder-a", root / "folder-b"]
    for folder in folders:
        folder.mkdir()
    started = []
    try:
        print("-- two folders, one port --")
        first = start(folders[0], 0, "process in folder-a")
        started.append(first)
        line = read_line(first)
        print(line.rsplit(" ", 1)[0])
        second = start(folders[1], bound_port(line), "process in folder-b")
        started.append(second)
        print(read_line(second))
        print("-- each folder asks the operating system for a free port --")
        lines = []
        for folder in folders:
            process = start(folder, 0, f"process in {folder.name}")
            started.append(process)
            lines.append(read_line(process))
        print("\n".join(text.rsplit(" ", 1)[0] for text in lines))
        print("ports differ:", len({bound_port(text) for text in lines}) == len(lines))
    finally:
        stop(started)


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
