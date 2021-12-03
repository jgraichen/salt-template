# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

import textwrap


def _text(text: str):
    return textwrap.dedent(text).lstrip()


def test_render(mods, render):
    out = render()

    assert out == _text(
        """
        # This file is managed by salt. Changes will be overwritten.

        {}
        """
    )


def test_render_source(mods, render):
    out = render(source="key")

    assert out == _text(
        """
        # This file is managed by salt. Changes will be overwritten.

        some:
          data: 1
        """
    )


def test_render_root(mods, render):
    out = render(source="key", root="app:config")

    assert out == _text(
        """
        # This file is managed by salt. Changes will be overwritten.

        app:
          config:
            some:
              data: 1
        """
    )
