#!/usr/bin/env python
import pathlib


def get_secret_key(strict: bool = True) -> str | None:
    f = pathlib.Path(__file__).parent.parent / "secret.txt"
    if f.exists():
        return f.read_text()
    if strict:
        raise RuntimeError("not found secret key")
    return None
