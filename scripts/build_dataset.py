#!/usr/bin/env python3
"""Build the processed connectivity dataset from the raw simulation folders.

Run once (or whenever the raw data changes)::

    python scripts/build_dataset.py \
        --sighted-dir /path/to/FM_Action/Sighted \
        --blind-dir   /path/to/FM_Action/Blind \
        --tally-baseline /path/to/Tally/P1_0.csv

Writes ``data/connectivity_data.csv``, which is all the analysis needs.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make the `connectivity` package importable when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from connectivity.config import PROCESSED_DATA
from connectivity.data import build_dataset, save_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sighted-dir", required=True, type=Path,
                        help="Directory of Sighted subject result folders.")
    parser.add_argument("--blind-dir", required=True, type=Path,
                        help="Directory of Blind subject result folders.")
    parser.add_argument("--tally-baseline", required=True, type=Path,
                        help="CSV with the pre-computed P1 presentation-0 baseline.")
    parser.add_argument("--out", type=Path, default=PROCESSED_DATA,
                        help=f"Output CSV (default: {PROCESSED_DATA}).")
    args = parser.parse_args()

    data = build_dataset(args.sighted_dir, args.blind_dir, args.tally_baseline)
    path = save_dataset(data, args.out)
    print(f"Built dataset: {len(data):,} rows → {path}")


if __name__ == "__main__":
    main()
