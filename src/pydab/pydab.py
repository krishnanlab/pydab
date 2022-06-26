import struct
from itertools import combinations
from typing import List, Literal, Optional, Tuple

import numpy as np


class PyDab:
    def __init__(
        self,
        filepath: Optional[str] = None,
        mode: Literal["dab", "dat"] = "dab",
    ):
        self._num_genes = 0
        self._gene_ids: List[str] = []
        self._size = 0
        self._weights = np.zeros(0, np.float32)

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

    def _load_dab(self, filepath):
        with open(filepath, "rb") as f:
            self._raw = f.read()

        self._num_genes = struct.unpack("<I", self._raw[:4])[0]
        self._size = self._num_genes * (self._num_genes - 1) // 2
        self._weights = np.zeros(self._size, dtype=np.float32)

        # Read gene ids
        name = b""
        slice_ = slice(5, -(self._size * 4 + 1))
        for i, char_pair in enumerate(struct.iter_unpack("2c", self._raw[slice_])):
            if char_pair == (b"\x00", b"\x00"):
                # TODO: make static
                # TODO: log to debug
                gene_id = name.decode()
                self.gene_ids.append(gene_id)
                name = b""
            elif char_pair[1] == b"\x00":
                name += char_pair[0]
            else:
                # TODO: check correctness of the calculated loc
                loc = 7 + i * 2
                raise ValueError(
                    f"Byte {loc} should be '0x00', got {char_pair[1]} instead",
                )
        gene_id = name.decode()
        self.gene_ids.append(gene_id)

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

    def _load_dat(self, filepath):
        pass

    def load(self, filepath: str, mode: Literal["dab", "dat"] = "dab"):
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

    def export(self, filepath):
        pass
