# FM-Action analysis (Blind vs Sighted)

Analysis code for the FM-Action brain-constrained modelling paper, comparing
**Blind** and **Sighted** neural-network simulations across learning, for two
paradigms (**P1**, **P2**). Reorganised from the original working notebooks into
small, reproducible packages.

## Paper

> **Visual cortex recruitment in blind individuals: Phonological, action or
> semantic representation? A deep brain-constrained neural network simulation**
>
> Maxime Carriere<sup>1,\*</sup>, Rosario Tomasello<sup>1,2,3</sup>
>
> <sup>1</sup> Brain Language Laboratory, Department of Philosophy and Humanities,
> WE4, Freie Universität Berlin, 14195 Berlin, Germany
> <sup>2</sup> Cognitive Sciences, Department of Psychology, University of
> Potsdam, Potsdam, Germany
> <sup>3</sup> Cluster of Excellence "Matters of Activity. Image Space Material",
> Humboldt-Universität zu Berlin, 10099 Berlin, Germany
> <sup>\*</sup> Corresponding author: carriere.maxime93@gmail.com
>
> **Keywords:** Congenital Blindness · Hebbian Learning · Visual Cortex ·
> Computational modelling · Semantic processing

The study investigates **when** visual-cortex recruitment for language first
emerges in congenital blindness — during pre-symbolic sensorimotor and
phonological word-form learning, or only after words acquire meaning through
semantic learning — using brain-constrained neural-network (BCN) modelling of 12
cortical areas. Phase 1 models action execution and phonological word-form
learning; Phase 2 models symbolic word–meaning association.

The model itself is available for NEST at
[github.com/MaximeCarriere/cogninest](https://github.com/MaximeCarriere/cogninest).

Two independent analyses live here:

* **`connectivity/`** — inter-area connectivity (summed connection strength
  between the 12 areas): connectivity matrices, Blind−Sighted differences,
  training-change heatmaps, condition contrasts, and network-level system-pair
  t-tests.
* **`activation/`** — time-course activation (number of active neurons per area
  over time-steps): the 2×6 per-area response grids, half-max (FWHM) window
  detection, Condition × System × AreaType repeated-measures ANOVA
  (Greenhouse-Geisser corrected), and per-area post-hoc t-tests.

## Paradigms

* **P1 — Phase 1** (initial learning): sensorimotor **Action** execution
  (patterns 1–6) and phonological **word-form / WF** learning (patterns 7–12),
  in separate network instances. Analysed at presentation **5000**.
* **P2 — Phase 2** (symbolic associative learning): word–meaning mapping,
  analysed across presentations, with statistics at presentation **50**.

A *presentation* is a learning episode; a *network* (`Net`) is one simulated
subject (22 retained per condition).

## Areas, systems and area-types

The 12 areas are grouped both by functional **system** and by **AreaType**
(the two within-subject factors of the activation ANOVA):

| System        | Areas         |   | AreaType    | Areas             |
|---------------|---------------|---|-------------|-------------------|
| Visual        | V1, TO, AT    |   | Primary     | V1, M1L, A1, M1I  |
| Motor         | PFL, PML, M1L |   | Secondary   | TO, PML, AB, PMI  |
| Auditory      | A1, AB, PB    |   | Central     | AT, PFL, PB, PFI  |
| Articulatory  | PFI, PMI, M1I |   |             |                   |

Definitions live in `connectivity/constants.py` and `activation/constants.py`.

## Layout

```
fm_action_analysis/
├── connectivity/                       # inter-area connectivity package
│   ├── constants.py  config.py  data.py
│   ├── aggregate.py  stats.py  plotting.py
├── activation/                         # time-course activation package
│   ├── constants.py  config.py  data.py
│   ├── window.py  stats.py  plotting.py
├── scripts/
│   ├── build_dataset.py                # raw → data/connectivity_data.csv
│   └── build_activation.py             # raw → data/activation_{p1,p2}.csv
├── notebooks/
│   ├── connection_analysis.ipynb
│   └── activation_analysis.ipynb
├── data/                               # generated datasets (gitignored)
└── figures/                            # generated figures, JPEG (gitignored)
    ├── connectivity/
    └── activation/
```

## Setup

Requires Python 3.9+ with the packages in `requirements.txt`
(`pandas numpy scipy statsmodels seaborn matplotlib jupyter`).

```bash
pip install -r requirements.txt
```

Developed with the `data_report` conda environment; select it as the notebook
kernel.

## Usage

Each analysis reads a pre-processed table. The raw simulation folders are only
needed once, by the build scripts — their paths are never hard-coded anywhere
else, so the committed code contains no absolute paths.

### 1. Build the datasets (once)

```bash
python scripts/build_dataset.py \
    --sighted-dir /path/to/FM_Action/Sighted \
    --blind-dir   /path/to/FM_Action/Blind \
    --tally-baseline /path/to/Tally/P1_0.csv

python scripts/build_activation.py --paradigm P1 --sighted-dir … --blind-dir …
python scripts/build_activation.py --paradigm P2 --sighted-dir … --blind-dir …
```

This writes `data/connectivity_data.csv` and `data/activation_{p1,p2}.csv`.

### 2. Run the analysis

Open the notebooks in `notebooks/` and run top to bottom, or use the packages
directly:

```python
# connectivity
from connectivity import load_dataset, area_connectivity, undirected_bidir, plotting
from connectivity.stats import system_pair_blind_vs_sighted_by_net

data = load_dataset()
undirected = undirected_bidir(area_connectivity(data))
plotting.plot_connectivity_triangle(undirected, "P1", "Sighted", presentation=0, vmax=1000)
system_pair_blind_vs_sighted_by_net(data, "P1", presentation=5000)

# activation
from activation import load_activation, activation_window, plotting as ap
from activation.stats import activation_rm_anova, activation_posthoc

frame = load_activation("P1")
win = activation_window(frame, presentation=5000, spe="WF")
ap.plot_timecourse_grid(frame, "P1", 5000, spe="WF", window=win)
res = activation_rm_anova(frame, win, presentation=5000, spe="WF")
activation_posthoc(res["ab"])          # Bonferroni-corrected, adjusted α = .0042
```

Figures are written to `figures/{connectivity,activation}/` as JPEG and shown
inline.
