#!/usr/bin/env python
import click
from pydantic import ValidationError
from rich import print
from qiandao.core.utils import ErrorConverter
from qiandao.core.mgr import QianDao


@click.command()
@click.option("-c", "--config", default="qiandao.yaml")
@click.option("--scheduled", default=False, is_flag=True)
def main(config: str, scheduled: bool):
    qd = QianDao(config)
    qd.run(scheduled)


if __name__ == "__main__":
    try:
        main()
    except ValidationError as e:
        print(ErrorConverter(e))
