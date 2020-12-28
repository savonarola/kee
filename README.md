## KeePass Helper

This is a script which does the following:

* Allows to find an entity in KDBX base with `fzf`.
* Copies its `password` to the clipboard.
* Prints `login` and `url` to stdout.

Works only for Macs.

### Installation

```bash
brew install fzf
pip install .
```

### Usage

```bash
kee-find --db "$SOME_PATH/base.kdbx"
```

```bash
security find-generic-password -a "$USER" -s "$ITEM_NAME" -w | kee-find -p --db "$SOME_PATH/base.kdbx"
```
