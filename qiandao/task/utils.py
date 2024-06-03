#!/usr/bin/env python
from pydantic import ValidationError

from rich.scope import render_scope
from rich.panel import Panel
from rich.table import Table


class ErrorConverter:

    def __init__(self, error: ValidationError):
        self.error = error

    def __rich__(self):
        table = Table.grid(padding=(0, 1), expand=False)
        for i, e in enumerate(self.error.errors(include_url=False)):
            title = ".".join([str(i) for i in e["loc"]])
            table.add_row(render_scope(e, title=title))

        return Panel.fit(
            table,
            title=f"{self.error.title} Validation Error",
            border_style="traceback.border"
        )

    def __str__(self):
        msg = [f"ValidationError [{self.error.title}]:"]
        for e in self.error.errors(include_url=False):
            loc = ".".join([str(i) for i in e["loc"]])
            msg.append(
                " - %s: %s, %s" % (loc, e["type"], e["msg"])
            )

        return "\n".join(msg)
