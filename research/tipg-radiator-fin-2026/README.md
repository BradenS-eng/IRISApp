# Ti-PG Radiator-Fin Analysis Archive

This directory preserves the manuscript-specific analysis and plotting scripts
used for the 2026 titanium-encapsulated pyrolytic graphite (Ti-PG) tube-fin
study. It supplements IRISApp; it is not part of the desktop application's
runtime workflow.

## Scope and boundaries

- Included: data-reduction and plotting source code, fixed test identifiers,
  plotting settings, and the thermal-exposure protocol schematic.
- Not included: raw infrared data, sensor logs, the effective-conductivity
  workbook, manuscript drafts, reviewer material, supplier documents, or
  generated result figures.
- The scripts reproduce research figures only when the authorized local input
  data and workbook are available. They do not establish uncertainty,
  calibration, or flight qualification beyond the associated manuscript.

## Included scripts

| Script | Primary output or purpose |
| --- | --- |
| `scripts/generate_fig4_revised.py` | Representative time histories and thermograph (IRIS-TF-084). |
| `scripts/generate_ti_only_comparison.py` | Ti-PG snap-on profiles: IRIS-TF-045–049 and IRIS-TF-056. |
| `scripts/generate_ti_only_TF077-081_TF084_comparison.py` | Ti-only profiles: IRIS-TF-077–081 and IRIS-TF-084. |
| `scripts/generate_hip_precycle_TF094-099_comparison.py` | HIP Ti-PG profiles before baking: IRIS-TF-094–099. |
| `scripts/generate_hip_thermal_cycle_comparison.py` | HIP before/after-bake profile comparison and final-frame sensitivity output. |
| `scripts/generate_hip_thermal_cycling_kin_comparison.py` | Six-state HIP profile comparison: pre-bake, baked, and 1-, 2-, 5-, and 10-cycle states. |
| `scripts/generate_effective_kin_bar_plot.py` | Mean and standard-deviation bar chart of effective in-plane conductivity. |
| `scripts/generate_hip_thermal_cycling_effective_kin.py` | Effective in-plane conductivity versus cumulative cycle count. |
| `scripts/generate_thermal_exposure_protocol.py` | Schematic of the prescribed 298–550 K bake and cycling programs. |

`k_in` in these scripts is an inverse-model-derived effective in-plane
heat-spreading property of the assembled fin. It is not the intrinsic bulk
conductivity of titanium or pyrolytic graphite.

## Local inputs

Before running a script that reads experimental data, set the following local
environment variables. They intentionally keep institution-specific paths and
unreleased data outside the repository.

```powershell
$env:IRISAPP_TIPG_DATA_ROOT = 'D:\authorized-data\Tube_Fin_Flow_Tests'
$env:IRISAPP_TIPG_WORKBOOK = 'D:\authorized-data\IRIS_effective_kin_data.xlsx'
```

The data root must contain one directory per test, such as `IRIS-TF-099`, with
the corresponding `.fts` file. The workbook must retain the documented data
layout expected by the two conductivity-summary scripts.

Run scripts from this directory so their sibling imports resolve correctly:

```powershell
cd research\tipg-radiator-fin-2026\scripts
python generate_hip_thermal_cycling_kin_comparison.py
python generate_hip_thermal_cycling_effective_kin.py
```

Generated files are written to `research/tipg-radiator-fin-2026/outputs/`,
which is intentionally ignored by Git.

## Thermal-exposure protocol

The bake and nominal cycle both use 10 K/min ramps between 298 and 550 K. The
bake includes a 60 min dwell at 550 K; the nominal cycle begins cooling when
550 K is reached. The protocol script is a schematic of the prescribed program,
not a measured specimen-temperature record.

## Software environment

The repository's `requirements.txt` supplies the scientific Python packages
needed by these scripts, including NumPy, SciPy, Matplotlib, Astropy, Pandas,
and OpenPyXL. Use Python 3.11 or newer where feasible.
