# Public recipe search log

Search date: 2026-08-23

Scope: peer-reviewed supported-catalyst preparation methods with enough explicit
information to audit ImpregCalc 0.1.0. Searches covered general web results, Europe
PMC full text, PubMed Central records, publisher pages/PDFs, and article method and
table text. The core selection rule was definition completeness, not numerical
agreement.

Representative query groups included:

- `"g of support" "incipient wetness" "mL" nitrate catalyst wt%`
- `"with respect to the mass of the support" iron nitrate impregnation`
- `controlled loading Nb2O5/(Nb2O5 + Al2O3) NbCl5`
- `incipient wetness co-impregnation cobalt nitrate platinum nitrate pore volume`
- `atomic ratio promoter incipient wetness catalyst precursor`
- `multi-cycle impregnation nitrate hydrate nominal loading ICP`
- searches by candidate PMCID, DOI, title, precursor notation, and methods phrases

## Screened records

| ID | Variation sought | Decision | Main reason |
|---|---|---|---|
| IC-PUB-001 | Anhydrous Pd complex; reported support and liquid masses | Definition audit | Loading denominator absent; reported liquid differs from pore-volume product |
| IC-PUB-002 | Hydrated Fe nitrate; support-relative elemental loading | Regression | Denominator and hydrate are explicit; measured liquid and assay remain unreported |
| IC-PUB-003 | Anhydrous NbCl5; final-basis oxide loading; nominal vs ICP | Regression | Formula, denominator, support mass, pore volume, and nominal/ICP distinction explicit |
| IC-PUB-004 | Multimetal Co/Pt co-impregnation; promoter by elemental wt% | Regression | Final elemental weight contents and pore volume explicit; pure-equivalent scope only |
| IC-PUB-005 | Co/Pt/Si, two Co/Pt steps plus separate Si step | Rejected | Denominator, support mass, per-cycle split, assays, and liquids incomplete |
| IC-PUB-006 | Hydrated Mg/Ni plus Ru; two-cycle MgO; reported Ni assay | Rejected | Printed neutral-salt stoichiometry and loading bases are ambiguous; liquid data absent |

## Selection notes

- A reported nominal percentage and an ICP/elemental-analysis value are different
  fields. IC-PUB-003 keeps them separate.
- “Promoted” in a paper does not imply an atomic-ratio input. IC-PUB-004 reports Pt
  by elemental weight content, so the validation models Pt as a second loading target,
  not as an invented Pt:Co atomic ratio.
- Multi-step language alone is insufficient for a cycle regression. IC-PUB-005 and
  IC-PUB-006 were rejected because individual step allocations are not reported.
- A formula that looks chemically suspect is not silently corrected. IC-PUB-006 did
  not trigger a parser change.
- Pd(acac)2 is an established abbreviation rather than a parseable elemental formula.
  The validation adapter expands it to `C10H14O4Pd` using PubChem CID 5486778; this
  alias is not added to the scientific core.

Full citations, licenses, remote file names, checksums, and exact validation scope are
in [`public-data-sources.json`](public-data-sources.json). Reasons and software actions
are in [`failure-register.json`](failure-register.json).
