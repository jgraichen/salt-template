#!py
# vim: ft=python:sw=4
"""
Python template to serialize an ini/properties file
"""

import configparser
import io
from typing import TYPE_CHECKING, Callable, Dict

if TYPE_CHECKING:
    __salt__: Dict[str, Callable]


def run():
    """
    Renders data into an ini/properties file.

    See `template.prepare` for context arguments on loading data, and
    `template.managed` for additional arguments when rendering the output.

    Example:

        /etc/application/config.ini:
          file.managed:
            - template: py
            - source: salt://_templates/ini.py
            - context:
                source:
                  - pillar_a
                  - pillar_b
                default:
                  DEFAULT:
                    key: 1

    Output:

        # Preamble

        [DEFAULT]
        key=1

        [section]
        from_pillar='Multiline
        string'
    """
    args = globals().get("context", {})
    data = __salt__["template.prepare"](**args)

    cfp = configparser.ConfigParser(interpolation=None)
    for section, items in sorted(data.items()):
        if not isinstance(items, dict):
            raise ValueError(
                f"INI section data in {section} must be dict but is {type(items).__name__}"
            )
        if section.lower() != "default":
            cfp.add_section(section)
        for key, value in sorted(items.items()):
            if value is None:
                continue
            if isinstance(value, list):
                value = ",".join([str(val) for val in value])
            cfp.set(section, key, str(value))

    try:
        buffer = io.StringIO()
        cfp.write(buffer)

        lines = buffer.getvalue().splitlines()
    finally:
        buffer.close()

    return __salt__["template.managed"](lines, **args)
