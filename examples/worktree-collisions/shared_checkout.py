#!/usr/bin/env python3
"""Two writers edit one file. First in one checkout, then in separate worktrees. Uses throwaway repos."""
import pathlib
import subprocess
import tempfile

ORIGINAL = "title: draft\nowner: nobody\n" + "note: unchanged\n" * 3 + "status: open\n"


def git(cwd, *args, check=True):
    env = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"}
    result = subprocess.run(
        ["git", "-c", "user.name=demo", "-c", "user.email=demo@example.invalid", "-c", "commit.gpgsign=false",
         "-c", "init.defaultBranch=main", *args],
        cwd=cwd, env=env, capture_output=True, text=True, check=False,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr)
    return result


def new_repo(root, name):
    repo = root / name
    repo.mkdir()
    git(repo, "init", "-q")
    (repo / "notes.txt").write_text(ORIGINAL)
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "start")
    return repo


def edit(text, key, value):
    return "".join(f"{key}: {value}\n" if line.startswith(key + ":") else line for line in text.splitlines(keepends=True))


def one_checkout(repo):
    path = repo / "notes.txt"
    seen_by_a = path.read_text()
    seen_by_b = path.read_text()
    path.write_text(edit(seen_by_a, "owner", "writer A"))
    path.write_text(edit(seen_by_b, "status", "writer B"))
    print("-- one checkout, both writers read before either wrote --")
    print(path.read_text(), end="")
    print("git status:", git(repo, "status", "--short").stdout.strip())


def two_worktrees(repo, key_b, value_b):
    for name, key, value in (("a", "owner", "writer A"), ("b", key_b, value_b)):
        tree = repo.parent / f"{repo.name}-tree-{name}"
        git(repo, "worktree", "add", "-q", "-b", f"agent/{name}", str(tree), "main")
        (tree / "notes.txt").write_text(edit((tree / "notes.txt").read_text(), key, value))
        git(tree, "commit", "-q", "-am", f"writer {name}")
    git(repo, "merge", "-q", "agent/a")
    merged_b = git(repo, "merge", "agent/b", check=False)
    print(f"-- two worktrees, writer B edits '{key_b}' --")
    print("merge of branch b, exit code:", merged_b.returncode)
    print((repo / "notes.txt").read_text(), end="")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp).resolve()
        one_checkout(new_repo(root, "shared"))
        two_worktrees(new_repo(root, "apart"), "status", "writer B")
        two_worktrees(new_repo(root, "clash"), "owner", "writer B")


if __name__ == "__main__":
    main()
