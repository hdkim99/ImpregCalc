# Validation record

## Current validation classes

The automated suite includes:

- direct formula composition and molar-mass checks for four common hydrated nitrate
  precursors;
- a hand-calculated elemental Co final-basis recipe;
- a hand-calculated Co3O4 conversion from cobalt nitrate;
- a support-relative loading whose numerical result differs from final basis;
- coupled Co/Ru final-basis co-impregnation;
- a Ru:Co atomic-ratio check performed by independently converting output masses
  back to molar amounts;
- 98% purity scaling while retaining the same pure-precursor requirement;
- exact support + retained-component mass closure;
- equal and custom arithmetic cycle allocation;
- nominal IWI and explicit wet-impregnation liquid volumes;
- invalid/zero loadings, missing promoter references, unsupported formulas, and a
  composition with no positive support fraction;
- JSON, Markdown, CSV, and XLSX exports;
- CLI operation without Tkinter or matplotlib import;
- GUI calculation, result display, export, close, and process exit.

Run:

```bash
pytest
```

## Public real-data validation

Status: **pending**.

A suitable publication method must unambiguously report all of support mass, target
loading convention, precursor hydrate state, assay, and enough liquid-volume detail
for the same calculation. No synthetic fixture in this repository is described as a
public experimental dataset. When a dataset is added, record DOI, license, citation,
checksum, files/rows used, and exact validation scope here.

## Definition differences

Literature phrases such as “15 wt% Co/Al2O3” are often insufficient by themselves to
distinguish support-relative from final-catalyst basis. ImpregCalc will not choose a
definition merely to reproduce a reported number. A validation case is accepted only
when the source or author-provided metadata resolves the definition.

