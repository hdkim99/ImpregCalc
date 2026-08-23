# Scientific basis and definitions

## Scope

ImpregCalc implements stoichiometric recipe arithmetic for incipient-wetness and wet
impregnation of a supplied support. It does not model the physical chemistry of
adsorption, pore filling, drying, calcination, or activation.

Munnik, de Jongh, and de Jong distinguish wet impregnation, where excess solution is
used, from pore-volume/incipient-wetness impregnation, where an amount intended to
fill support pore volume is used. They also discuss how precursor–support
interactions and drying affect the ultimate spatial distribution. This is why the
software labels `support mass × pore volume` as a **nominal planning volume**, not a
guarantee of complete or uniform pore filling.

## Loading definitions

Let:

- `S` be initial dry support mass in g;
- `M` be the modeled final formulated mass, `S` plus all named retained components;
- `c_j` be the retained mass of component `j`;
- `w_j` be the user-entered loading percentage divided by 100.

For a final-catalyst-basis target:

```text
c_j = w_j M
```

For a support-relative target:

```text
c_j = w_j S
```

The common mass balance is:

```text
M = S + sum(c_j)
```

The simultaneous linear relation is solved once, so multiple final-basis targets and
support-relative targets are not calculated independently with inconsistent
denominators. If the derived retained-component fraction leaves no positive support
fraction, calculation fails.

`final_catalyst` is a calculation convention here: support plus all explicitly named
retained components. Purity impurities, counterions removed during conversion, and
unmodeled processing residues are not included. The output always repeats this
definition.

## Element, oxide, and precursor targets

For precursor `P`, active component `A`, and target element `E`, let `n_P,E` and
`n_A,E` be atoms of `E` in each formula unit. Assuming quantitative conversion and
retention of the requested active component, active mass obtainable per gram of pure
precursor is:

```text
y = (n_P,E / n_A,E) MW_A / MW_P
```

Then:

```text
m_P,pure = c_A / y
m_P,commercial = m_P,pure / purity_fraction
```

For an elemental target, `A` is the element. For an oxide target, `A` is the exact
oxide formula provided by the user. For a precursor target, `A = P` and `y = 1`.
This arithmetic is why `15 wt% Co`, `15 wt% Co3O4`, and `15 wt% Co nitrate` cannot
share one ambiguous input mode.

Quantitative conversion is an explicit assumption, not a yield prediction. If the
real thermal treatment produces another phase, loses volatile target species, or
does not retain all precursor, the requested recipe model must be reconsidered.

## Atomic-ratio promoter

For promoter element `Q` specified at atomic ratio `r = n_Q / n_E` to a named
reference component `A`:

```text
c_Q = r c_A (n_A,E / MW_A) AW_Q
```

Promoter mass participates in the same final mass balance. Promoters cannot form a
chain in version 0.1.0; every promoter refers to a primary loading target.

## Hydrate formula and atomic weights

The parser accepts neutral integer-stoichiometry formulas, parentheses/brackets, and
hydrate components separated by `·`, `∙`, `•`, or ASCII `.`. A leading integer on a
hydrate segment is a multiplier. For example, `Co(NO3)2·6H2O` gives Co:1, N:2,
O:12, H:12.

Atomic masses are conventional abridged values in g mol⁻¹ based on the IUPAC 2021
standard atomic-weight table. Some elements have interval standard atomic weights in
normal terrestrial materials; ImpregCalc uses a single documented conventional value
and does not propagate natural-isotope variation. Isotopically enriched substances
are outside scope.

## Liquid and concentration reporting

For IWI:

```text
nominal solution volume / mL = support mass / g × pore volume / (mL g^-1)
```

An explicitly supplied solution volume may override this product and is reported as
an override. Wet-impregnation mode always requires an explicit volume. Concentration
outputs are commercial precursor mass per selected total solution volume and pure
precursor molarity.

No undocumented concentration threshold is applied. The program never calls a
concentrated recipe soluble or insoluble. Solubility depends on solvent, temperature,
pH, speciation, impurities, and co-solutes and must be checked experimentally or
against a separately validated data source.

## Multi-cycle convention

Cycle fractions allocate every precursor mass and the selected total liquid volume.
Equal fractions are the default. This is only reproducible recipe arithmetic; it is
not a claim that one and several impregnation/drying/calcination cycles produce
identical pore distributions, crystallite sizes, or catalytic behavior.

## References

1. P. Munnik, K. P. de Jongh, and K. P. de Jong, “Recent Developments in the
   Synthesis of Supported Catalysts,” *Chemical Reviews* **115** (2015) 6687–6718.
   <https://doi.org/10.1021/cr500486u>.
2. C. Perego and P. Villa, “Catalyst preparation methods,” *Catalysis Today* **34**
   (1997) 281–305. <https://doi.org/10.1016/S0920-5861(96)00055-7>.
3. F. Pinna, “Supported metal catalysts preparation,” *Catalysis Today* **41**
   (1998) 129–137. <https://doi.org/10.1016/S0920-5861(98)00043-1>.
4. T. Prohaska et al., “Standard atomic weights of the elements 2021 (IUPAC
   Technical Report),” *Pure and Applied Chemistry*. IUPAC table and report link:
   <https://iupac.qmul.ac.uk/AtWt/AtWt21.html>.

References 1–3 establish preparation-method terminology and physical limitations.
The loading, purity, atomic-ratio, and mass-balance equations above are direct
stoichiometric derivations rather than empirical correlations.

