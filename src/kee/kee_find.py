import argparse
from pykeepass import PyKeePass
from pyfzf.pyfzf import FzfPrompt
from argparse import ArgumentParser
from getpass import getpass
import sys
import plumbum
import subprocess


def write_to_clipboard(text):
    process = subprocess.Popen(
        "pbcopy", env={"LANG": "en_US.UTF-8"}, stdin=subprocess.PIPE
    )
    process.communicate(text.encode("utf-8"))


def select_path(paths):
    fzf = FzfPrompt()

    try:
        paths = fzf.prompt(paths)
    except plumbum.commands.processes.ProcessExecutionError:
        paths = None

    if not paths:
        print("Nothing selected", file=sys.stderr)
        sys.exit(0)

    (path,) = paths

    return path


def get_password(args):
    if args.password_from_stdin:
        password = input()
    else:
        password = getpass()

    return password


def output_entry(entry):
    print(entry.title)
    print("username:", entry.username)
    print("url:     ", entry.url)
    if entry.password:
        write_to_clipboard(entry.password)


def main():
    parser = ArgumentParser("kee-find")
    parser.add_argument("--db", required=True, type=argparse.FileType("r"))
    parser.add_argument(
        "--password-from-stdin", "-p", default=False, action="store_true"
    )

    args = parser.parse_args()

    password = get_password(args)

    db = PyKeePass(args.db.name, password=password)

    entries = db.entries
    path = select_path(e.path for e in entries)

    (entry,) = (e for e in entries if e.path == path)

    output_entry(entry)


if __name__ == "__main__":
    main()
