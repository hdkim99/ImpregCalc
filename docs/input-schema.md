# JSON input guide

Required top-level fields are `support_name`, `support_mass_g`, `method`, and a
non-empty `targets` list.

Each loading target requires:

- `name`: unique label;
- `kind`: `elemental_metal`, `metal_oxide`, or `precursor`;
- `basis`: `final_catalyst` or `support_relative`;
- `loading_percent`: percentage value, not a fraction;
- `active_formula`: required for oxide, optional for elemental or precursor;
- `precursor.formula`, `precursor.target_element`, and optional
  `precursor.purity_fraction` in `(0, 1]`.

`incipient_wetness` requires `pore_volume_ml_g`. Optional `solution_volume_ml`
explicitly overrides the nominal product. `wet_impregnation` requires
`solution_volume_ml` and does not require pore volume.

Optional `cycles` defaults to one. Optional `cycle_fractions` must contain one
positive fraction per cycle and sum to one.

Promoters require `target_element`, `reference_target`,
`atomic_ratio_to_reference`, and a precursor. The ratio is promoter atoms per one
reference-target-element atom.

See [`examples/co_ru_iwi.json`](../examples/co_ru_iwi.json) and
[`examples/nickel_oxide_wet.json`](../examples/nickel_oxide_wet.json).

