#!py
# vim: ft=python:sw=4
"""
Python template to serialize an ENV file
"""

import shlex
from typing import TYPE_CHECKING, Callable, Dict

if TYPE_CHECKING:
    __salt__: Dict[str, Callable]


def run():
    """
    Renders data into an ENV file.

    See `template.prepare` for context arguments on loading data, and
    `template.managed` for additional arguments when rendering the output.

    Example:

        /etc/default/env:
            file.managed:
                - template: py
                - source: salt://_templates/env.py
                - context:
                    source:
                        - pillar_a
                        - pillar_b
                    default:
                        KEY: 1
                        KEY: 2

    Output:

        # Preamble

        KEY=1
        KEY=2
        KEY_FROM_PILLAR='Multiline
        string'
    """
    args = globals().get("context", {})
    data = __salt__["template.prepare"](**args)

    lines = []
    for k, v in data.items():
        if isinstance(v, list):
            v = " ".join(v)

        lines.append(f"{k}={shlex.quote(str(v))}")

    return __salt__["template.managed"](lines, **args)
