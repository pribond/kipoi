"""Test the CLI interface
"""
import keras  # otherwise I get a segfault from keras ?!
import pytest
import sys
import os
import yaml
from contextlib import contextmanager
import modelzoo
from modelzoo.data import numpy_collate
# from torch.utils.data import DataLoader


# TODO - check if you are on travis or not regarding the --install-req flag
INSTALL_FLAG = "--install-req"
# INSTALL_FLAG = ""

EXAMPLES_TO_RUN = ["rbp", "extended_coda"]


@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def read_json_yaml(filepath):
    with open(filepath) as ifh:
        return yaml.load(ifh)


def get_extractor_cfg(model_dir):
    return read_json_yaml(os.path.join(model_dir, 'extractor.yaml'))


def get_test_kwargs(model_dir):
    return read_json_yaml(os.path.join(model_dir, 'test_files/test.json'))


@pytest.mark.parametrize("example", EXAMPLES_TO_RUN)
def test_extractor_model(example):
    """Test extractor
    """
    if example == "rbp" and sys.version_info[0] == 2:
        pytest.skip("rbp example not supported on python 2 ")

    example_dir = "examples/{0}".format(example)
    cfg = get_extractor_cfg(example_dir)

    modelzoo.data.validate_extractor_spec(cfg["extractor"])
    test_kwargs = get_test_kwargs(example_dir)

    # get extractor
    Extractor = modelzoo.load_extractor(example_dir)

    # get model
    model = modelzoo.load_model(example_dir)

    with cd(example_dir + "/test_files"):
        # initialize the extractor
        extractor = Extractor(**test_kwargs)
        # get first sample
        extractor[0]
        len(extractor)
        modelzoo.data.validate_extractor(extractor)

        # sample a batch of data
        batch = numpy_collate([extractor[i] for i in range(5)])

        # current BUG in pytorch
        # ../../../miniconda/envs/test-environment/lib/python2.7/site-packages/torch/__init__.py:53: in <module>
        #     from torch._C import *
        # E   ImportError: dlopen: cannot load any more object with static TLS
        # -----
        # dl = DataLoader(extractor, collate_fn=numpy_collate)
        # it = iter(dl)
        # batch = next(it)
        # predict with a model
        model.predict_on_batch(batch["inputs"])
