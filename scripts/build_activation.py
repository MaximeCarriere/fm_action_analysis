#!/usr/bin/env python3
"""Build the processed activation table for a paradigm from the raw folders.

Run once per paradigm (or whenever the raw data changes)::

    python scripts/build_activation.py --paradigm P1 \
        --sighted-dir /path/to/FM_Action/Sighted \
        --blind-dir   /path/to/FM_Action/Blind

Writes ``data/activation_p1.csv`` (or ``_p2.csv``), which is all the analysis
needs. Each paradigm reads a different raw neuron file (see activation.constants).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from activation.data import build_activation, save_activation


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--paradigm", required=True, choices=["P1", "P2"])
    parser.add_argument("--sighted-dir", required=True, type=Path,
                        help="Directory of Sighted subject result folders.")
    parser.add_argument("--blind-dir", required=True, type=Path,
                        help="Directory of Blind subject result folders.")
    args = parser.parse_args()

    data = build_activation(args.paradigm, args.sighted_dir, args.blind_dir)
    path = save_activation(data, args.paradigm)
    print(f"Built {args.paradigm}: {len(data):,} rows → {path}")


if __name__ == "__main__":
    main()
