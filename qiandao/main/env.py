#!/usr/bin/env python
import environ
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent

ENV = environ.Env(
    DJANGO_SETTINGS_MODULE=(str, "main.settings")
)
