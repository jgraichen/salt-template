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
        """
    )


def test_render_source(mods, render):
    out = render(source="key")

    assert out == _text(
        """
        # This file is managed by salt. Changes will be overwritten.

        Some text.
        """
    )


def test_render_source_blank(mods, render):
    out = render(source="empty")

    assert out == _text(
        """
        # This file is managed by salt. Changes will be overwritten.
        """
    )


def test_render_source_multiple(mods, render):
    out = render(source="blob1,blob2", comment_prefix="//")

    assert out == _text(
        """
        // This file is managed by salt. Changes will be overwritten.

        // blob1
        blob1


        // blob2
        blob2
        """
    )


def test_render_source_comment(mods, render):
    out = render(source="key", comment="This is\na comment.")

    assert out == _text(
        """
        # This file is managed by salt. Changes will be overwritten.

        # This is
        # a comment.

        Some text.
        """
    )
