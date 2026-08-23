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

Status: **published-method arithmetic validated; laboratory reproduction not
verified**.

Three published supported-catalyst methods now provide definition-resolved numerical
regressions. A fourth paper is retained as a dual-definition audit because it does not
state the loading denominator. These are public research method records, not new
impregnation experiments and not evidence that ImpregCalc predicts catalyst structure.

The machine-readable provenance, retrieved-file checksum, license, exact facts used,
and exclusions are in
[`validation/public-data-sources.json`](../validation/public-data-sources.json). The
decision trail, including rejected candidates, is in
[`validation/failure-register.json`](../validation/failure-register.json), and the
queries and candidate screen are in
[`validation/search-log.md`](../validation/search-log.md). Original article files are
not redistributed.

### IC-PUB-002 — support-relative Fe, hydrated precursor

Mosallanejad et al. explicitly define approximately 3 wt% Fe **with respect to support
mass**, use iron(III) nitrate nonahydrate, and report a 0.47 cm³/g pore volume for
gamma-alumina. Because their support batch mass is not reported, the regression uses
the scale-independent basis of 1.000 g dry support:

```text
m(Fe) = 1.000 g support × 0.03 = 0.030000 g
M[Fe(NO3)3·9H2O] = 403.992 g/mol
m(pure precursor) = 0.030000 × 403.992 / 55.845
                  = 0.2170249799 g
nominal IWI volume = 1.000 × 0.47 = 0.470 mL
```

The authors describe adding liquid until paste-like consistency and do not report the
measured volume. Therefore 0.470 mL is validated only as ImpregCalc's nominal
pore-volume product. Precursor assay is absent, so the validated mass is a pure
equivalent, not a commercial mass-to-weigh claim.

Reference: Mosallanejad et al., *ACS Omega* 3 (2018), DOI
[`10.1021/acsomega.8b00201`](https://doi.org/10.1021/acsomega.8b00201).

### IC-PUB-003 — final-basis Nb2O5 and nominal/ICP separation

Jiao et al. define the controlled loading as
`Nb2O5/(Nb2O5 + Al2O3)`, report 0.500 g support, use NbCl5, and give a
0.63 cm³/g pore volume for unloaded gamma-alumina. For their controlled 10 wt%
case:

```text
m(final formulated) = 0.500 / (1 - 0.10) = 0.5555555556 g
m(Nb2O5 target) = 0.0555555556 g
M(NbCl5) = 270.15637 g/mol
m(pure NbCl5) = 0.1129288953 g
nominal IWI volume = 0.500 × 0.63 = 0.315 mL
```

Table 1 reports 4.7 wt% by ICP-AES for the catalyst whose controlled loading was
10 wt%. The regression intentionally feeds **10 wt% nominal** to the recipe engine
and stores **4.7 wt% measured** only as an observation. It does not back-calculate
retention or silently relabel the measured value as a target.

Reference: Jiao et al., *Scientific Reports* 6 (2016), DOI
[`10.1038/srep34068`](https://doi.org/10.1038/srep34068).

### IC-PUB-004 — Co/Pt co-impregnation

Karaca et al. report incipient-wetness co-impregnation using
`Co(NO3)2·6H2O` and `Pt(NH3)4(NO3)2`, a support pore volume of
0.477 cm³/g, and catalyst weight contents of 10 wt% Co and 0.05 wt% Pt. A
1.000 g support normalization exercises the coupled final-catalyst denominator:

```text
m(final formulated) = 1.000 / (1 - 0.10 - 0.0005)
                    = 1.1117287382 g
m(Co) = 0.1111728738 g
m(Pt) = 0.0005558644 g
m(pure cobalt nitrate hexahydrate) = 0.5490076477 g
m(pure tetrammineplatinum nitrate) = 0.0011033174 g
shared nominal IWI volume = 0.477 mL
```

The shared liquid volume appears on both precursor rows and is not summed. Assays,
actual masses, and measured solution volume are absent, so only theoretical
pure-equivalent arithmetic and mass closure are validated.

Reference: Karaca et al., *Comptes Rendus Chimie* 12 (2009), DOI
[`10.1016/j.crci.2008.09.028`](https://doi.org/10.1016/j.crci.2008.09.028).

### IC-PUB-001 — Pd(acac)2 definition audit, not a gold regression

Corral et al. report 0.030 g Pd(acac)2, 1.000 g support, 5.0 mL acetone,
and “1.0 wt% Pd” without a denominator. PubChem CID 5486778 supplies the expanded
formula [`C10H14O4Pd`](https://pubchem.ncbi.nlm.nih.gov/compound/5486778) for the
source abbreviation. ImpregCalc therefore preserves two scenarios:

```text
1.0 wt% final-catalyst basis  -> 0.0289151618 g pure Pd(acac)2
1.0 wt% support-relative     -> 0.0286260101 g pure Pd(acac)2
reported                     -> 0.0300000000 g Pd(acac)2
```

With the same atomic weights, the reported mass corresponds to 1.0480 wt% Pd/support
or 1.0371 wt% Pd/(support + retained Pd), compatible with a rounded 1.0 wt% claim but
not sufficient to identify its convention. For PMS, the reported 5.0 mL is 4.31 times
the reported 1.16 cm³/g pore-volume product. This is recorded as a discrepancy; no
unreferenced feasibility threshold is applied and the paper's terminology is not
silently rewritten.

Reference: Corral et al., *Materials* 6 (2013), DOI
[`10.3390/ma6041554`](https://doi.org/10.3390/ma6041554).

## Candidate failures

- **IC-PUB-005:** a Co–Pt–Si multi-step method was examined, but loading denominator,
  support mass, per-cycle allocation, assays, and actual liquid volumes are not all
  defined. It is not a numerical regression.
- **IC-PUB-006:** a Mg/Ni/Ru method includes useful hydrate, purity, and multi-cycle
  details, but prints `Ni(NO3)·6H2O` and `Mg(NO3)·6H2O` in parts of the method and
  omits loading denominators and liquid quantities. ImpregCalc does not silently
  correct the formulas or invent cycle splits.

No hydrate parser change was needed: all accepted explicit hydrate formulas parse
with the existing dot-notation implementation. Publication notation normalization
is confined to the validation-only preprocessor outside `src/impregcalc`.

## Definition differences

Literature phrases such as “15 wt% Co/Al2O3” are often insufficient by themselves to
distinguish support-relative from final-catalyst basis. ImpregCalc will not choose a
definition merely to reproduce a reported number. A validation case is accepted only
when the source or author-provided metadata resolves the definition.
