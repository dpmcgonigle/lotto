# ########################################################################################
#  Copyright 2020 Systems & Technology Research.                                         #
#                                                                                        #
#  Systems & Technology Research Proprietary.                                            #
#                                                                                        #
#  This (data/software) was developed pursuant to Prime Contract Number                  #
#  FA8650-19-C-1030 with the US Government. The US Government shall have unlimited       #
#  rights license to this (data/software).                                               #
#                                                                                        #
#  This (document/software) contains Technical Data subject to the Arms Export Control   #
#  Act, Title 22 USC Sec 2778 et seq., or the Export Administration Act of 1979,         #
#  as amended, Title 50, U.S.C. App 2401 et seq. and the International Traffic in Arms   #
#  Regulations, 22 CFR 120-130. Violations of these laws are subject to severe criminal  #
#  penalties. Disseminate in accordance with provisions of DoD Directive 5230.25.        #
#                                                                                        #
#  Distribution authorized to US Government agencies and their contractors. Other        #
#  requests for this document shall be referred to AFRL/RYA                              #
# ########################################################################################
import os

import boto3
import pytest
from moto import mock_s3


def _get_curdir() -> str:
    """Returns current directory"""
    return os.path.dirname(os.path.realpath(__file__))


def basedir() -> str:
    """Returns base directory for repo"""
    return os.path.join(_get_curdir(), "..")


@pytest.fixture
def train_specification_path() -> str:
    return "data/test/config/train_titanic_sparkrfc.json"


@pytest.fixture
def train_gridsearch_specification_path() -> str:
    return "data/test/config/train_gridsearch_titanic_sparkrfc.json"


@pytest.fixture
def eval_specification_path() -> str:
    return "data/test/config/eval_titanic_sparkrfc.json"


@pytest.fixture
def output_config_path() -> str:
    return "data/test/output/config_output.json"


@pytest.fixture
def dest_bucket_name() -> str:
    return "DEST_BUCKET"


@pytest.fixture
def moto_s3(dest_bucket_name):
    # setup: start moto server and create the bucket
    mocks3 = mock_s3()
    mocks3.start()
    res = boto3.resource("s3")
    res.create_bucket(Bucket=dest_bucket_name)
    yield
    # teardown: stop moto server
    mocks3.stop()
