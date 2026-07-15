# FM-Action analysis (Blind vs Sighted)

Analysis code for the FM-Action modelling paper, comparing **Blind** and
**Sighted** neural-network simulations across training, for two paradigms
(**P1**, **P2**). Reorganised from the original working notebooks into small,
reproducible packages.

Two independent analyses live here:

* **`connectivity/`** — inter-area connectivity (summed connection strength
  between the 12 areas): connectivity matrices, Blind−Sighted differences,
  training-change heatmaps, condition contrasts, and network-level system-pair
  t-tests.
* **`activation/`** — time-course activation (number of active neurons per area
  over time-steps): the 2×6 per-area response grids, half-max window detection,
  Condition × System × Area repeated-measures ANOVA (Greenhouse-Geisser
  corrected), and per-area post-hoc t-tests.

### Areas and functional systems

The 12 areas are grouped into four functional systems (3 areas each):

| System        | Areas            |
|---------------|------------------|
| Visual        | V1, TO, AT       |
| Motor         | PFL, PML, M1L    |
| Auditory      | A1, AB, PB       |
| Articulatory  | PFI, PMI, M1I    |

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

Developed against the `data_report` conda environment.

## Usage

Each analysis reads pre-processed tables; the raw simulation folders are only
needed once, by the build scripts, and their paths are never hard-coded elsewhere.

### Connectivity

```bash
python scripts/build_dataset.py \
    --sighted-dir /path/to/FM_Action/Sighted \
    --blind-dir   /path/to/FM_Action/Blind \
    --tally-baseline /path/to/Tally/P1_0.csv
```

```python
from connectivity import load_dataset, area_connectivity, undirected_bidir, plotting
from connectivity.stats import system_pair_blind_vs_sighted_by_net

data = load_dataset()
undirected = undirected_bidir(area_connectivity(data))
plotting.plot_connectivity_triangle(undirected, "P1", "Sighted", presentation=0, vmax=1000)
system_pair_blind_vs_sighted_by_net(data, "P1", presentation=5000)
```

### Activation (time-course)

```bash
python scripts/build_activation.py --paradigm P1 --sighted-dir … --blind-dir …
python scripts/build_activation.py --paradigm P2 --sighted-dir … --blind-dir …
```

```python
from activation import load_activation, activation_window, plotting
from activation.stats import activation_rm_anova, activation_posthoc

frame = load_activation("P1")
win = activation_window(frame, presentation=5000, spe="WF")
plotting.plot_timecourse_grid(frame, "P1", 5000, spe="WF", window=win)
res = activation_rm_anova(frame, win, presentation=5000, spe="WF")
activation_posthoc(res["ab"])
```

Or open the notebooks in `notebooks/` and run top to bottom. Figures are written
to `figures/` (JPEG) and shown inline.
