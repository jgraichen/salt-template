# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,redefined-outer-name

import copy
import logging
import os
import tempfile

import pytest
import salt.config
import salt.loader
import salt.pillar
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PILLAR_DATA = {}


def _load_pillar(node):
    # Optional load pillar data from co-located file
    path = str(node.fspath)[:-3] + ".pillar.yaml"
    if path not in PILLAR_DATA:
        if os.path.exists(path):
            with open(path) as fd:
                data = yaml.safe_load(fd) or {}
        else:
            data = {}

        PILLAR_DATA[path] = data

    if node.name in PILLAR_DATA[path]:
        return PILLAR_DATA[path][node.name]
    return PILLAR_DATA[path].get("test", {})


@pytest.fixture
def tmpd():
    with tempfile.TemporaryDirectory() as directory:
        yield directory


@pytest.fixture
def opts(tmpd):
    opts = salt.config.minion_config(os.path.join(ROOT, "test/minion.yaml"))
    opts["cachedir"] = os.path.join(tmpd, "cache")
    opts["pki_dir"] = os.path.join(tmpd, "pki")
    opts["module_dirs"] = [ROOT, os.path.join(ROOT, "test/fixtures")]
    opts["file_roots"] = {"base": [ROOT]}

    return opts


@pytest.fixture
def utils(opts):
    return salt.loader.utils(opts)


@pytest.fixture
def mods(request, opts, utils):
    # Assign pillar data for current test
    new_opts = copy.deepcopy(opts)
    new_opts["pillar"] = _load_pillar(request.node)
    return salt.loader.minion_mods(new_opts, utils=utils)


@pytest.fixture
def renderers(opts, mods):
    return salt.loader.render(opts, mods)


@pytest.fixture
def render(request, renderers):
    name = request.node.module.__name__[5:]

    def render_fn(**context):
        kwargs = {}
        if context:
            kwargs["context"] = context

        return salt.template.compile_template(
            template=os.path.join(ROOT, f"_templates/{name}.py"),
            renderers=renderers,
            default="jinja|yaml",
            blacklist=None,
            whitelist=None,
            **kwargs,
        )

    return render_fn


@pytest.fixture(autouse=True)
def debug_log_level(caplog):
    caplog.set_level(logging.DEBUG)
