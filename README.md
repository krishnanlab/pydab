<p align="center">
  <img src="dab.png" />
</p>

# pydab
A (_blazing fast_?) Python package for modifying and converting DAB files

## Installation

```bash
pip install pydab
```

Alternatively, install the latest dev version from github

```bash
pip install git+https://github.com/krishnanlab/pydab
```

## Quick start

Convert a DAB file to a DAT file, i.e., tab separated edgelist file with three columns.

```txt
Gene1 Gene2 Weight12
Gene1 Gene3 Weight13
...
```

To convert a DAB file `data.dab` into `data.dat`, simply run

```bash
pydab -i data.dab -o data.dat
```

## Some up-coming features
- [ ] DAT -> DAB
- [ ] Export to `.npz` dense array
- [ ] Export to `.npz` CSR (directly supported by PecanPy)
- [ ] More
