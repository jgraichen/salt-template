#!py
# vim: ft=python:sw=4
"""
Python template to serialize a sysctl-like configuration
"""


def run():
    """
    Renders data into a sysctl-like configuration file.

    See `template.prepare` for context arguments on loading data, and
    `template.managed` for additional arguments when rendering the output.

    Example:

        /etc/sysctl.conf:
            file.managed:
                - template: py
                - source: salt://_templates/sysctl.py
                - context:
                    source:
                        - pillar_a
                        - pillar_b
                    default:
                        key.one: 1
                        key.two: 2

    Output:

        # Preamble

        key.one = 1
        key.two = 2
    """
    args = globals().get('context', {})
    data = __salt__["template.prepare"](**args)

    lines = []
    for key, value in data.items():
        if isinstance(value, bool):
            lines.append(f"{key} = {str(value).lower()}")
        elif isinstance(value, list):
            for index, part in enumerate(value):
                lines.append(f"{key}.{index + 1} = {part}")
        else:
            lines.append(f"{key} = {value}")

    return __salt__["template.managed"](lines, **args)
