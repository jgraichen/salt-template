# vim: ft=python
"""
Utility functions for working with templates and template-based file
serialization.
"""

import inspect


def _fastmerge(a, b):
    """
    Fast recursive merge of dicts and list.

    Fast merge avoids copying dicts and list but also avoids mutating
    objects. It operates by rebuilding nested datasets from top to
    bottom if necessary.
    """
    if isinstance(a, dict) and isinstance(b, dict):
        if not b:  # If B is empty we can return A
            return a

        # Prepare new dict with everything in A that is not in B and therefore
        # does not need to be rebuild.
        data = {k: v for k, v in a.items() if k not in b}

        for k, v in b.items():
            # Merge everthing in A and B but only copy things from B that are
            # not in A.
            data[k] = _fastmerge(a[k], v) if k in a else v

        return data

    if isinstance(a, list) and isinstance(b, list):
        # Lists are just appended
        return [*a, *b]

    return b


def _filter(data, exclude=None):
    if not exclude:
        return data
    if isinstance(data, dict):
        return {k: _filter(v, exclude) for k, v in data.items() if k not in exclude}
    if isinstance(data, list):
        return [_filter(v) for v in data]
    return data


def _pillar_get(key, *args, **kwargs):
    """
    Read a pillar key like `pillar.get`, but with salt's pillar masking
    disabled.

    Salt 3008 redacts the values returned by `pillar.get` unless the
    caller opts out. The jinja and mako renderers clear the masking
    context so that templates receive the real values, the `py` renderer
    does not. All arguments are passed through to `pillar.get`.
    """

    pillar_get = __salt__["pillar.get"]

    if "unmask" in inspect.signature(pillar_get).parameters:
        kwargs["unmask"] = True

    return pillar_get(key, *args, **kwargs)


def _render_commented(text, sign):
    lines = [f"{sign} {line.rstrip()}" for line in text.strip().splitlines()]

    if lines:
        lines.append("")

    return lines


def managed(text, comment=None, comment_prefix="#", preamble=True, **_kwargs):
    """
    Takes a string or list of lines and renders a final configuration
    file. It will add a preamble acquired via
    `config.get("template_managed")`. The default is the following text:

        This file is managed by salt. Changes will be overwritten.

    All lines in the preamble will be prefixed with the given sign
    (default `#`) and prepended to the text. The preamble, the given
    text or lines, and a final newline are joined together and returned.
    """

    if isinstance(text, list):
        text = "\n".join(text).strip()

    lines = []
    if comment_prefix:
        if preamble:
            preamble = __salt__["config.get"](
                "template_managed",
                "This file is managed by salt. Changes will be overwritten.",
            )
            lines.extend(_render_commented(preamble, comment_prefix))

        if comment:
            lines.extend(_render_commented(comment, comment_prefix))

    lines.append(text)
    return "\n".join(lines).strip() + "\n"


def prepare(**kwargs):
    """
    Prepares a dataset for serialize template.

    Takes default data and merges datasets from multiple sources from pillar.
    Used in serialize templates for getting the initial data.
    """

    data = kwargs.get("default", {})
    exclude = kwargs.get("exclude", [])

    if "source" in kwargs:
        sources = kwargs["source"]

        if isinstance(sources, str):
            sources = [s.strip() for s in sources.split(",")]

        for key in sources:
            data = _fastmerge(data, _pillar_get(key, default={}))

    if exclude:
        if isinstance(exclude, str):
            exclude = [exclude]
        if not isinstance(exclude, list):
            raise ValueError("exclude must be a list")
        data = _filter(data, exclude)

    return data
