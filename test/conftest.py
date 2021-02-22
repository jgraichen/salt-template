# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,redefined-outer-name

import logging
import os
import tempfile
import copy

import pytest
import yaml

import salt.config
import salt.loader
import salt.pillar

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PILLAR_DATA = {}


def _load_pillar(node):
    # Optional load pillar data from colocated file
    path = str(node.fspath)[:-3] + ".pillar.yaml"
    if path not in PILLAR_DATA:
        if os.path.exists(path):
            with open(path) as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}

        PILLAR_DATA[path] = data

    if node.name in PILLAR_DATA[path]:
        return PILLAR_DATA[path][node.name]
    return PILLAR_DATA[path].get("test", {})


@pytest.fixture
def tmpd():
    with tempfile.TemporaryDirectory() as d:
        yield d


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


@pytest.fixture()
def mods(request, opts, utils):
    # Assign pillar data for current test
    o = copy.deepcopy(opts)
    o["pillar"] = _load_pillar(request.node)
    return salt.loader.minion_mods(o, utils=utils)

@pytest.fixture()
def render(request, mods):
    name = request.node.module.__name__[5:]
    def fn(**context):
        if context:
            return mods['slsutil.renderer'](f'salt://_templates/{name}', context=context)
        else:
            return mods['slsutil.renderer'](f'salt://_templates/{name}')
    return fn


@pytest.fixture(autouse=True)
def debug_log_level(caplog):
    caplog.set_level(logging.DEBUG)
