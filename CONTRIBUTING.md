# Contributing

Thank you for improving ImpregCalc. Do not put unpublished, proprietary,
export-controlled, or otherwise confidential research data in a public issue or pull
request.

## Scientific changes

Every scientific-core change must state:

1. the equation or definition and the convention it implements;
2. every input/output unit and loading denominator;
3. assumptions, validity range, and unsupported cases;
4. an original publication, established textbook, or peer-reviewed review when the
   change is not a direct dimensional/stoichiometric derivation;
5. an independent numerical validation (hand calculation, literature benchmark, or
   controlled synthetic benchmark);
6. boundary and invalid-input behavior plus a regression test.

Do not add an undocumented coefficient, threshold, uncertainty, or confidence claim.
Do not infer model validity from R² alone.

## GUI and plotting changes

Record the supported platform, dependency change, backend impact, macOS smoke result,
and proof that CLI/core imports remain GUI-independent. Do not add Qt without a
documented need, one binding only, clean-environment macOS lifecycle validation, and
explicit backend checks.

## Local checks

```bash
python -m pip install -e ".[dev,plot]"
ruff format --check .
ruff check .
mypy src
pytest
python -m build
twine check dist/*
```

