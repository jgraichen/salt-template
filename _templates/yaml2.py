#!py
# vim: ft=python:sw=4
"""
Python template for YAML serialization
"""

from typing import TYPE_CHECKING, Callable, Dict

import yaml as _pyyaml
from salt.serializers import yaml

if TYPE_CHECKING:
    __salt__: Dict[str, Callable]

try:
    from salt.utils.versions import version_cmp
except ImportError:
    from salt.utils import version_cmp


def run():
    """
    Serializes into YAML file.

    See `template.prepare` for context arguments on loading data, and
    `template.managed` for additional arguments when rendering the output.

    Arguments:

    root (str, optional): A colon separated string to nest all data before
        serializing to YAML.

    Example:

        /etc/app/config.yaml:
          file.managed:
            - template: py
            - source: salt://_templates/yaml2.py
            - context:
                source: app:config
                root: app:production
                default:
                  cache:
                    default: value

    Output:

        # Preamble

        app:
          production:
            cache:
              pillar: value
              default: value
    """
    args = globals().get("context", {})
    data = __salt__["template.prepare"](**args)

    if "root" in args:
        for level in reversed(args["root"].split(":")):
            data = {level: data}

    # sort_keys only exists in newer pyyaml versions
    if version_cmp(_pyyaml.__version__, "5.1") >= 0:
        out = yaml.serialize(data, default_flow_style=False, sort_keys=False)
    else:
        out = yaml.serialize(data, default_flow_style=False)

    return __salt__["template.managed"](out, **args)
