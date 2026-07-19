# WhakerPy tests

## Install required dependencies

```bash
> python -m pip install ".[tests]"
```

## Launch tests

Run from the repository root, not from this "tests" folder: `whakerpy` must
be importable, which only works when the current directory is the repo root.

```bash
> python -m unittest discover -s tests
```

The last printed line should be "OK".


## Analyze tests coverage

Also run from the repository root:

```bash
> coverage run
```

It creates a .coverage file. 
Then, see results in the terminal, and write XML report to tests/coverage.xml with:

```bash
> coverage report -m
> coverage xml
```
