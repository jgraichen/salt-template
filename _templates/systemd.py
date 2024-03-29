#!py
# vim: ft=python:sw=4
"""
Python template to serialize a systemd.syntax file
"""

from typing import TYPE_CHECKING, Callable, Dict

if TYPE_CHECKING:
    __salt__: Dict[str, Callable]


def _escape(string: str):
    return "\\\n    ".join(string.splitlines())


def _value(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, str):
        return _escape(value)
    if isinstance(value, (int, float)):
        return str(value)
    raise ValueError(f"Unsupport value: {value!r}")


def _render_section(name, values):
    lines = [f"[{name}]"]

    for key, value in values.items():
        if isinstance(value, list):
            for val in value:
                lines.append(f"{key}={_value(val)}")
        else:
            lines.append(f"{key}={_value(value)}")

    lines.append("")
    return lines


def run():
    """
    Renders data into a systemd syntax file.

    See `template.prepare` for context arguments on loading data, and
    `template.managed` for additional arguments when rendering the output.

    Arguments:

    section (str): Render key value pairs from data into this section instead of
        using the top dict for sections. Nested dicts are not supported.

    Example:

        /etc/systemd/system/unit.service:
            file.managed:
                - template: py
                - source: salt://_files/serialize/systemd.py
                - context:
                    default:
                        Unit:
                            Description: "A Unit Description"
                        Service:
                            ExecStart:
                                - command
                                - command

    Output:

        # Preamble

        [Unit]
        Description=A Unit Description

        [Service]
        ExecStart=command
        ExecStart=command
    """
    args = globals().get("context", {})
    data = __salt__["template.prepare"](**args)

    if "section" in args:
        data = {args["section"]: data}

    lines = []
    for name, values in data.items():
        if isinstance(values, list):
            for items in values:
                lines.extend(_render_section(name, items))
        else:
            lines.extend(_render_section(name, values))

    return __salt__["template.managed"](lines, **args)
