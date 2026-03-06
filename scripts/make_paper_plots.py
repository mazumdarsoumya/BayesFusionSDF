import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

dst = Path("result_paper/plots")
dst.mkdir(parents=True, exist_ok=True)

df = pd.read_csv("outputs/ablations_fixed/summary_iso.csv")

# Plot 1: F@20 by anchor
g = df.groupby("anchor")["f@20mm"].mean().reset_index()
plt.figure()
plt.bar(g["anchor"].astype(str), g["f@20mm"])
plt.xlabel("anchor")
plt.ylabel("F@20mm")
plt.title("Iso-band F@20 vs anchoring")
plt.savefig(dst / "f20_by_anchor.png", dpi=200, bbox_inches="tight")
plt.close()

# Plot 2: NBV utility by anchor (log scale) for nbv=True
df_n = df[df["nbv"] == True].groupby("anchor")["nbv_utility"].mean().reset_index()
plt.figure()
plt.bar(df_n["anchor"].astype(str), df_n["nbv_utility"])
plt.yscale("log")
plt.xlabel("anchor")
plt.ylabel("NBV utility (log)")
plt.title("NBV utility vs anchoring")
plt.savefig(dst / "nbv_utility_by_anchor_log.png", dpi=200, bbox_inches="tight")
plt.close()

# Plot 3: Precision–Recall @20mm by anchor
pr = df.groupby("anchor")[["prec@20mm", "rec@20mm"]].mean().reset_index()
plt.figure()
plt.scatter(pr["prec@20mm"], pr["rec@20mm"])
for _, r in pr.iterrows():
    plt.text(r["prec@20mm"], r["rec@20mm"], str(r["anchor"]))
plt.xlabel("Precision @20mm")
plt.ylabel("Recall @20mm")
plt.title("Precision–Recall @20mm (iso_points)")
plt.savefig(dst / "prec_rec_20mm_anchor.png", dpi=200, bbox_inches="tight")
plt.close()

print("Wrote plots to:", dst)
