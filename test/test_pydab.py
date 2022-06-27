import pathlib

import pytest

from pydab import PyDab

CURRENT_PATH = pathlib.Path(__file__).absolute().parent
DATA_PATH = CURRENT_PATH.joinpath("data")

TOL = 6  # error tolerance


def test_pydab_case1():
    pdb = PyDab(DATA_PATH.joinpath("case1.dab"), log_level="DEBUG")

    assert pdb.num_genes == 4
    assert pdb.gene_ids == ["1", "2", "3", "4"]
    assert pdb.weights.astype(float).round(TOL).tolist() == [1, 0.2, 0.8, 0, 0, 0]


def test_pydab_case2():
    pdb = PyDab(DATA_PATH.joinpath("case2.dab"), log_level="DEBUG")

    assert pdb.num_genes == 3
    assert pdb.gene_ids == ["Gene1", "Gene2", "GENE9"]
    assert pdb.weights.astype(float).round(TOL).tolist() == [0.52, 0.9285, 1]
