# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

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
    out = render(source="service")

    assert out == _text(
        """
        # This file is managed by salt. Changes will be overwritten.

        [Unit]
        Description=A common service unit file
        After=consul.service
        After=nomad.service

        [Service]
        Type=simple
        ExecStart=
        ExecStart=/usr/bin/env
        """
    )


def test_render_section(render):
    out = render(source="config", section="Resolve")

    assert out == _text(
        """
        # This file is managed by salt. Changes will be overwritten.

        [Resolve]
        DNS=127.0.0.1
        Domains=~consul
        """
    )
