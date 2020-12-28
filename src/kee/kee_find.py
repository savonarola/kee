import argparse
import pykeepass
from pyfzf.pyfzf import FzfPrompt
from argparse import ArgumentParser
from getpass import getpass
import sys
import plumbum
import pyperclip
from rich.console import Console
from rich.table import Table


CONSOLE = Console()

CONSOLE_STDERR = Console(file=sys.stderr)


def abort(message, code=-1):
    CONSOLE_STDERR.print(f"[red]{message}")
    sys.exit(code)


def select_item(items):
    fzf = FzfPrompt()

    enumerated = (f"{n}.\t{item}" for (n, item) in enumerate(items))

    try:
        selected_items = fzf.prompt(enumerated, "-i")
    except plumbum.commands.processes.ProcessExecutionError:
        selected_items = None

    if not selected_items:
        abort("Nothing selected", code=0)

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
    properties = {}
    properties["Username"] = entry.username
    properties["Url"] = entry.url
    for key, value in entry.custom_properties.items():
        properties[key] = value
    properties["Notes"] = entry.notes

    table = Table()
    table.title = entry.title
    table.add_column("Field")
    table.add_column("Value")

    for key, value in properties.items():
        if value:
            table.add_row(key, value)

    CONSOLE.print(table)

    if entry.password:
        pyperclip.copy(entry.password)
        CONSOLE.print("Password copied to clipboard")


def output_field(name, value):
    if value:
        print(f"{name}: {value}")


def open_db(filename, password):
    try:
        with CONSOLE.status("[bold green]Opening DB"):
            db = pykeepass.PyKeePass(filename, password=password)
    except pykeepass.exceptions.CredentialsError:
        abort("Wrong credentials")

    return db


def main():
    parser = ArgumentParser("kee-find")
    parser.add_argument("--db", required=True, type=argparse.FileType("r"))
    parser.add_argument(
        "--password-from-stdin", "-p", default=False, action="store_true"
    )
    args = parser.parse_args()

    password = get_password(args)

    db = open_db(args.db.name, password)

    entries = db.entries
    idx = select_item(e.title for e in entries)

    entry = entries[idx]

    output_entry(entry)


if __name__ == "__main__":
    main()
