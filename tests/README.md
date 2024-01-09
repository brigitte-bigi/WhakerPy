# WhakerPy tests

## Install required dependencies

```bash
> cd tests 
> python -m pip install -r requirements.txt
```

## Launch tests

```bash
>python -m unittest discover
```

The last printed line should be "OK".


## Analyze tests coverage

```bash
>coverage run -m unittest discover
```

It creates a .coverage file. 
Then, see results in the terminal, and write XML report to tests/coverage.xml with:

```bash
>coverage report -m
>coverage xml
```
