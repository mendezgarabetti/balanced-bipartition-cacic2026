import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import os

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(_REPO_ROOT, "results")
OUT = os.path.join(RESULTS, "fig_gap_density.pdf")

df = pd.read_csv(f"{RESULTS}/gap_density_instances.csv")

fig, axes = plt.subplots(1, 2, figsize=(7, 2.3))

specs = [
    ("Synthetic", axes[0], "Synthetic 2D (sub300)", "o"),
    ("HCV", axes[1], "HCV (sub300)", "s"),
]

for dataset, ax, title, marker in specs:
    sub = df[df.Dataset == dataset]
    ax.scatter(sub["d_nn"], sub["pct_gap"], marker=marker, color="black", s=45, zorder=3)
    ax.set_title(title)
    ax.set_xlabel(r"mean 1-NN distance $d_{nn}$")
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=4))

axes[0].set_ylabel("optimality gap (%)")

fig.tight_layout()
fig.savefig(OUT)
print("saved", OUT)
