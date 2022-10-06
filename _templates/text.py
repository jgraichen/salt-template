#!py
# vim: ft=python:sw=4
"""
Python template to serialize a text file
"""

from types import NoneType
from typing import TYPE_CHECKING, Callable, Dict

if TYPE_CHECKING:
    __salt__: Dict[str, Callable]

VALID_TYPES = (str, NoneType)

def run():
    """
    Serializes one or more text parts into a file.

    See `template.managed` for additional arguments when rendering the output.

    Arguments:

    default (str, optional): A default text rendered as first part.

    source (str, list, optional): A comma-separated string or list of pillar
        keys that are to be rendered.
    """
    lines = []
    args = globals().get("context", {})
    prefix = args.get("comment_prefix", "#")

    if "default" in args:
        lines.append(args["default"])

    sources = args.get("source", [])

    if isinstance(sources, str):
        sources = [s.strip() for s in sources.split(",")]

    for key in sources:
        data = __salt__["pillar.get"](key)

        if data is None:
            continue

        if isinstance(data, list):
            if all(isinstance(item, VALID_TYPES) for item in data):
                data = "\n".join(filter(lambda value: isinstance(value, str), data))

        if isinstance(data, dict):
            if all(isinstance(value, VALID_TYPES) for value in data.values()):
                data = "\n".join(filter(lambda value: isinstance(value, str), data.values()))

        if not isinstance(data, str):
            raise ValueError(
                f"Pillar value at {key} must be a str, but is {type(data)}"
            )

        if prefix and not data and len(sources) > 1:
            lines.append(f"{prefix} Omitted blank blob: {key}")

        if data:
            if prefix and len(sources) > 1:
                lines.append(f"{prefix} {key}")
            lines.append(data)
            lines.append("\n")

    return __salt__["template.managed"](lines, **args)
