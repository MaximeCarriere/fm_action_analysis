# Inter-area connectivity analysis (Blind vs Sighted)

Analysis code for the inter-area connectivity results comparing **Blind** and
**Sighted** neural-network simulations across training, for two paradigms
(**P1**, **P2**). Reorganised from the original working notebook into a small,
reproducible package.

## What it does

For each simulated network (subject) the raw output gives the summed connection
strength between every pair of the 12 modelled areas, at a series of training
*presentations*. This code:

1. reads all subjects into one tidy table (once), then
2. aggregates to mean area-pair connectivity, and produces the paper figures and
   statistics: connectivity matrices, Blind−Sighted differences, training-change
   heatmaps, condition contrasts, per-network change bar plots, and network-level
   Blind-vs-Sighted t-tests over functional-system pairs.

### Areas and functional systems

The 12 areas are grouped into four functional systems (3 areas each):

| System        | Areas            |
|---------------|------------------|
| Visual        | V1, TO, AT       |
| Motor         | PFL, PML, M1L    |
| Auditory      | A1, AB, PB       |
| Articulatory  | PFI, PMI, M1I    |

Canonical ordering, colours and group definitions live in
[`connectivity/constants.py`](connectivity/constants.py).

## Layout

```
connectivity_analysis/
├── connectivity/            # reusable package
│   ├── constants.py         # area order, colours, systems, network→presentation maps
│   ├── config.py            # repo-relative paths (data/, figures/)
│   ├── data.py              # build / save / load the dataset
│   ├── aggregate.py         # area_connectivity, undirected_bidir, get_area_matrix
│   ├── stats.py             # system-pair test, within-group change test
│   └── plotting.py          # heatmaps + change bar plots
├── scripts/build_dataset.py # raw simulation folders → data/connectivity_data.csv
├── notebooks/connection_analysis.ipynb   # the analysis, section by section
├── data/                    # generated dataset (gitignored)
└── figures/                 # generated figures (gitignored)
```

## Setup

Requires Python 3.9+ with the packages in `requirements.txt`
(`pandas numpy scipy seaborn matplotlib jupyter`).

```bash
pip install -r requirements.txt
```

This project was developed against the `data_report` conda environment.

## Usage

### 1. Build the dataset (once)

Point the builder at the raw simulation folders and the P1 baseline; it writes a
single `data/connectivity_data.csv`:

```bash
python scripts/build_dataset.py \
    --sighted-dir   /path/to/FM_Action/Sighted \
    --blind-dir     /path/to/FM_Action/Blind \
    --tally-baseline /path/to/Tally/P1_0.csv
```

The raw paths are only needed here — nothing else in the repo hard-codes them.

### 2. Run the analysis

Open `notebooks/connection_analysis.ipynb` and run top to bottom, or use the
package directly:

```python
from connectivity import load_dataset, area_connectivity, undirected_bidir, plotting
from connectivity.stats import system_pair_blind_vs_sighted_by_net

data = load_dataset()
area_conn = area_connectivity(data)
undirected = undirected_bidir(area_conn)

plotting.plot_connectivity_triangle(undirected, "P1", "Sighted", presentation=0, vmax=1000)
system_pair_blind_vs_sighted_by_net(data, "P1", presentation=5000)
```

Figures are written to `figures/` (and displayed inline in the notebook).
