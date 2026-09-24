"""Additional GA repetitions for Synthetic/full and HCV/full, extending those
configurations from 3 to 30 runs so the Mann-Whitney test leaves its
combinatorial floor.

Same GA invocation and seed convention as run_ga_baseline.py, but on new seeds
and writing to separate "_extra" CSVs, leaving the original files untouched.
Runs tasks in parallel, one process per core.

Usage:
    python3 run_ga_baseline_extra.py --seed-start 45 --seed-end 71 --workers 28
"""
import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd

from common import get_synthetic_2d, get_hcv, run_ga_c2, RESULTS_DIR

GENERATIONS = 1000  # identical to run_ga_baseline.py -- see PROTOCOL.md
POP_SIZE = 100

LOADERS = {
    "Synthetic": get_synthetic_2d,
    "HCV": get_hcv,
}

# Repetition numbers for the original 3 runs are 1..3 (seeds 42..44);
# the extra runs continue the Repetition numbering from 4 onward, keyed by
# seed offset from 42 (so Repetition == seed - 41), for direct traceability
# back to run_ga_baseline.py's FULL_SEEDS = range(42, 72) convention.


def _run_one(dataset, seed):
    loader = LOADERS[dataset]
    X, desc = loader()
    M = len(X) // 2
    t0 = time.time()
    _, w_pos = run_ga_c2(X, M, generations=GENERATIONS, pop_size=POP_SIZE, seed=seed)
    t_exec = time.time() - t0
    row = {
        "Dataset": dataset, "Mode": "full", "N": len(X), "Seed": seed,
        "Repetition": seed - 41, "Generations": GENERATIONS,
        "W_pos": w_pos, "Time_s": t_exec,
    }
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-start", type=int, default=45)
    ap.add_argument("--seed-end", type=int, default=71)  # inclusive, matches FULL_SEEDS max
    ap.add_argument("--workers", type=int, default=28)
    ap.add_argument("--datasets", nargs="+", default=["Synthetic", "HCV"])
    args = ap.parse_args()

    seeds = list(range(args.seed_start, args.seed_end + 1))
    tasks = [(ds, s) for ds in args.datasets for s in seeds]
    print(f"Launching {len(tasks)} GA runs ({len(seeds)} seeds x {len(args.datasets)} datasets) "
          f"with {args.workers} parallel workers...", flush=True)

    results = {ds: [] for ds in args.datasets}
    t_start = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(_run_one, ds, s): (ds, s) for ds, s in tasks}
        done = 0
        for fut in as_completed(futs):
            ds, s = futs[fut]
            row = fut.result()
            results[ds].append(row)
            done += 1
            print(f"[{done}/{len(tasks)}] {ds} seed={s} rep={row['Repetition']} "
                  f"W_pos={row['W_pos']:.4f} time={row['Time_s']:.1f}s "
                  f"elapsed_total={time.time()-t_start:.1f}s", flush=True)

    for ds, rows in results.items():
        rows.sort(key=lambda r: r["Seed"])
        df = pd.DataFrame(rows)
        out_path = os.path.join(RESULTS_DIR, f"raw_ga_{ds}_full_extra.csv")
        df.to_csv(out_path, index=False)
        print(f"Saved {len(df)} extra reps -> {out_path}")

    print(f"Total wall time: {time.time()-t_start:.1f}s")


if __name__ == "__main__":
    main()
