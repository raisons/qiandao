#!/usr/bin/env python
import secrets
import os
import datetime
import pathlib

RANDOM_STRING_CHARS = ("abcdefghijklmnopqrstuvwxyz"
                       "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                       "0123456789")


def get_random_string(length: int = 64):
    return "".join(secrets.choice(RANDOM_STRING_CHARS) for i in range(length))


def generate():
    file = pathlib.Path("secret.txt")
    if file.exists():
        now = datetime.datetime.now()
        now = now.strftime("%Y%m%d%H%M%S")
        file.rename(f"secret_{now}.txt")
        file = pathlib.Path("secret.txt")

    with file.open("w") as fp:
        fp.write(get_random_string())


if __name__ == "__main__":
    generate()
