# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

import contextlib
import textwrap


def text(text: str):
    return textwrap.dedent(text).lstrip()


def test_managed(mods):
    out = mods["template.managed"]("TEXT")

    assert out == text(
        """
        # This file is managed by salt. Changes will be overwritten.

        TEXT
        """
    )


def test_managed_comment_prefix(mods):
    out = mods["template.managed"]([], comment_prefix="//")
    assert out == "// This file is managed by salt. Changes will be overwritten.\n"


def test_managed_comment_prefix_off(mods):
    out = mods["template.managed"](["TEXT"], comment_prefix=False)
    assert out == "TEXT\n"


def test_managed_preamble_config(mods):
    def stub(key, default):
        assert key == "template_managed"
        assert default == "This file is managed by salt. Changes will be overwritten."
        return "DO NOT EDIT"

    mods["config.get"] = stub
    out = mods["template.managed"]("")

    assert out == "# DO NOT EDIT\n"


def test_managed_preamble_off(mods):
    out = mods["template.managed"]([], preamble=False)
    assert out == "\n"


def test_managed_comment(mods):
    out = mods["template.managed"](["TEXT"], comment="This is\na comment.")

    assert out == text(
        """
        # This file is managed by salt. Changes will be overwritten.

        # This is
        # a comment.

        TEXT
        """
    )


def test_managed_comment_prefix_off(mods):
    out = mods["template.managed"](
        ["TEXT"], comment_prefix=False, comment="This is\na comment."
    )
    assert out == "TEXT\n"


def test_managed_lines_rstrip(mods):
    out = mods["template.managed"](["TEXT", "\n\n\n", ""], comment_prefix=False)
    assert out == "TEXT\n"


def test_prepare(mods):
    assert mods["template.prepare"]() == {}


def test_prepare_default(mods):
    assert mods["template.prepare"](default="DEFAULT") == "DEFAULT"


def test_prepare_source(mods):
    assert mods["template.prepare"](source="key") == {}


def test_prepare_source_pillar(mods):
    out = mods["template.prepare"](source="key")
    assert out == {"some": {"pillar": "data"}}


def test_prepare_source_pillar_colon(mods):
    out = mods["template.prepare"](source="a,b")
    assert out == {"a": 1, "b": 2}


def test_prepare_source_pillar_list(mods):
    out = mods["template.prepare"](source=["a", "b"])
    assert out == {"a": 1, "b": 2}


def test_prepare_source_merge(mods):
    out = mods["template.prepare"](source="a,b")
    assert out == {"a": 1, "b": 2, "key": {"name": "b"}, "value": 2}


def test_prepare_source_merge_default(mods):
    out = mods["template.prepare"](source="key", default={"v": {"i": 1}})
    assert out == {"v": {"i": 2}}
