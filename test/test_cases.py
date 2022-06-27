import filecmp
import pathlib

import pytest

from pydab import PyDab

CURRENT_PATH = pathlib.Path(__file__).absolute().parent
DATA_PATH = CURRENT_PATH / "data"

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


@pytest.mark.parametrize("name", ["case1", "case2"])
def test_pydab_export_case1(tmpdir, name):
    pdb = PyDab(DATA_PATH / f"{name}.dab", log_level="INFO")
    pdb.export(pathlib.Path(tmpdir) / f"{name}.dat")

    assert filecmp.cmp(tmpdir / f"{name}.dat", DATA_PATH / f"{name}.dat")
