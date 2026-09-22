import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
n_trials = 10000

joseph_hours = np.random.triangular(30, 40, 60, n_trials)
mel_hours = np.random.triangular(25, 35, 50, n_trials)
will_hours = np.random.triangular(25, 35, 55, n_trials)

n_blockers = np.random.poisson(1.5, n_trials)
blocker_hours = np.array([
    np.sum(np.random.uniform(3, 8, k)) if k > 0 else 0.0
    for k in n_blockers
])

total_hours = joseph_hours + mel_hours + will_hours + blocker_hours

THRESHOLD = 120
avg = np.mean(total_hours)
p10 = np.percentile(total_hours, 10)
p90 = np.percentile(total_hours, 90)
prob_exceed = np.mean(total_hours > THRESHOLD)

# Chart (matplotlib) - built from the numpy-generated total_hours array
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.hist(total_hours, bins=50, color="#4C72B0", edgecolor="white", alpha=0.85)
ax.axvline(THRESHOLD, color="#C44E52", linestyle="--", linewidth=2,
           label=f"2-week capacity threshold ({THRESHOLD} hrs)")
ax.axvline(avg, color="#55A868", linestyle="-", linewidth=2,
           label=f"Average ({avg:.0f} hrs)")
ax.set_xlabel("Total Development Time (hours)")
ax.set_ylabel("Number of Simulation Trials")
ax.set_title("Monte Carlo Simulation: Development Time (10,000 trials)")
ax.legend()
fig.tight_layout()
fig.savefig("monte_carlo_dev_time.png", dpi=150)