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


def select_item(items):
    fzf = FzfPrompt()

    enumerated = (f"{n}.\t{item}" for (n, item) in enumerate(items))

    try:
        selected_items = fzf.prompt(enumerated, "-i")
    except plumbum.commands.processes.ProcessExecutionError:
        selected_items = None

    if not selected_items:
        print("Nothing selected", file=sys.stderr)
        sys.exit(0)

    (selected_item,) = selected_items

    selected_index = int(selected_item.split(".")[0])

    return selected_index


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
        print("Password copied to clipboard")


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
    idx = select_item(e.title for e in entries)

    entry = entries[idx]

    output_entry(entry)


if __name__ == "__main__":
    main()
