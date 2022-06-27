import logging
import struct
from itertools import combinations
from typing import List, Literal, Optional, Tuple, Union

import numpy as np

MODES = Literal["dat", "dab", "npz"]

logger = logging.getLogger(__name__)


class PyDab:
    def __init__(
        self,
        filepath: Optional[str] = None,
        mode: MODES = "dab",
        log_level: Union[str, int] = "WARNING",
    ):
        self._num_genes = 0
        self._gene_ids: List[str] = []
        self._size = 0
        self._weights = np.zeros(0, np.float32)

        self.logger = logger.getChild(self.__class__.__name__)
        self.logger.setLevel(log_level)

        if filepath:
            self.load(filepath, mode)

    def __getitem__(self, pos: Tuple[int, int]):
        i, j = pos
        if min(i, j) < 0 or max(i, j) > self.num_genes:
            raise ValueError(
                f"Indices should be between 0 and {self.num_genes}, got {pos}",
            )

    @property
    def num_genes(self) -> int:
        return self._num_genes

    @property
    def gene_ids(self) -> List[str]:
        return self._gene_ids

    @property
    def size(self) -> int:
        return self._size

    @property
    def weights(self) -> np.ndarray:
        return self._weights

    def _new_gene_id(self, gene_id_byte: bytes):
        """Add new gene ID to the gene ID list."""
        gene_id = gene_id_byte.decode()
        self.gene_ids.append(gene_id)
        self.logger.debug(f"{gene_id=}")

    def _load_dab(self, filepath: str):
        with open(filepath, "rb") as f:
            self._raw = f.read()

        self._num_genes = struct.unpack("<I", self._raw[:4])[0]
        self._size = self._num_genes * (self._num_genes - 1) // 2
        self._weights = np.zeros(self._size, dtype=np.float32)

        # Read gene ids
        gene_id_byte = b""
        slice_ = slice(5, -(self._size * 4 + 1))
        for i, char_pair in enumerate(struct.iter_unpack("2c", self._raw[slice_])):
            if char_pair == (b"\x00", b"\x00"):
                self._new_gene_id(gene_id_byte)
                gene_id_byte = b""
            elif char_pair[1] == b"\x00":
                gene_id_byte += char_pair[0]
            else:
                # TODO: check correctness of the calculated loc
                loc = 7 + i * 2
                raise ValueError(
                    f"Byte {loc} should be '0x00', got {char_pair[1]} instead",
                )
        self._new_gene_id(gene_id_byte)

        if len(self.gene_ids) != self.num_genes:
            raise ValueError(
                f"Header indicates {self.num_genes} number of genes, ",
                f"but only {len(self.gene_ids)} genes loaded",
            )

        # TODO: break into chunks when reading
        chunk_size = self._size
        self._weights[:] = struct.unpack(
            f"<{chunk_size}f",
            self._raw[-(chunk_size * 4) :],
        )
        # Replace inf (unobserved edges) with zero edge weights
        np.nan_to_num(self._weights, copy=False, posinf=0)

    def _load_dat(self, filepath: str):
        raise NotImplementedError

    def load(self, filepath: str, mode: MODES = "dab"):
        # TODO: check file existence
        if mode == "dab":
            self._load_dab(filepath)
        elif mode == "dat":
            self._load_dat(filepath)
        else:
            raise ValueError(f"Unknown mode {mode}")

    def to_adjmat(self) -> np.ndarray:
        mat = np.array((self.num_genes, self.num_genes), dtype=np.float32)
        # TODO: improve this by copying one row (upper triang) at a time
        for w, (i, j) in zip(self._weights, combinations(range(self.num_genes), 2)):
            mat[i, j] = w
        return mat + mat.T

    def _export_dat(self, filepath: str, sep: str = "\t", **kwargs):
        with open(filepath, "w") as f:
            for w, (i, j) in zip(self._weights, combinations(range(self.num_genes), 2)):
                if w == 0:
                    self.logger.debug(f"Skipping zero entry ({i}, {j})")
                else:
                    self.logger.debug(f"Writting ({i}, {j}) entry with {w=}")
                    terms = sep.join([self.gene_ids[i], self.gene_ids[j], f"{w:g}"])
                    f.write(f"{terms}\n")
        self.logger.info(f"DAT (edgelist) file saved to {filepath}")

    def _export_dab(self, filepath: str, **kwargs):
        raise NotImplementedError

    def _export_npz(self, filepath: str, **kwargs):
        raise NotImplementedError

    def export(self, filepath: str, mode: MODES = "dat", **kwargs):
        if mode == "dat":
            self._export_dat(filepath, **kwargs)
        elif mode == "dab":
            self._export_dab(filepath, **kwargs)
        elif mode == "npz":
            self._export_npz(filepath, **kwargs)
        else:
            raise ValueError(f"Unknown mode {mode}")
