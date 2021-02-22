# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

import textwrap

import pytest


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

        some.key = 1
        some.other.key = 2
        some.list.1 = a
        some.list.2 = b
        """
    )
