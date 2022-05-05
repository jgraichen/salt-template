# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

import textwrap


def _text(text: str):
    return textwrap.dedent(text).lstrip()


def test_render(render):
    out = render()

    assert out == _text(
        """
        # This file is managed by salt. Changes will be overwritten.
        """
    )


def test_render_source(render):
    out = render(source="key")

    assert out == _text(
        """
        # This file is managed by salt. Changes will be overwritten.

        [DEFAULT]
        key = 1
        multiline = Multi
        \tline
        \tstring

        [section]
        decimal with space = 1.23
        dict = {'a': 1, 'b': 2}
        list = A,B
        """
    )
