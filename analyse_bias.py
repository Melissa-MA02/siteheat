"""Single-station check: is the forecast error at this site consistent, or noise?"""
import numpy as np
import pandas as pd

df = pd.read_csv("joined.csv", parse_dates=["date"])
e = df["error"]  # observed - forecast; positive = street hotter than forecast

n, mean, sd = len(e), e.mean(), e.std()
half_width = 1.96 * sd / np.sqrt(n)  # naive CI; consecutive days are correlated, so treat as optimistic

print(f"days: {n}")
print(f"mean error:   {mean:+.2f} C   (95% CI {mean - half_width:+.2f} to {mean + half_width:+.2f})")
print(f"median error: {e.median():+.2f} C")
print(f"spread (sd):  {sd:.2f} C")
print(f"days street was hotter: {(e > 0).mean():.0%}")
print(f"days beyond +/-1 C:     {(e.abs() > 1).mean():.0%}")

print("\nby season (mean error):")
season = {12: "summer", 1: "summer", 2: "summer", 3: "autumn", 4: "autumn", 5: "autumn",
          6: "winter", 7: "winter", 8: "winter", 9: "spring", 10: "spring", 11: "spring"}
df["season"] = df["date"].dt.month.map(season)
for name, grp in df.groupby("season"):
    print(f"  {name:<7} {grp['error'].mean():+.2f} C   (n={len(grp)})")

print("\nby forecast temperature (this is where it matters):")
bins = [-np.inf, 20, 25, 30, 35, np.inf]
labels = ["<20", "20-25", "25-30", "30-35", "35+"]
df["band"] = pd.cut(df["forecast_max"], bins=bins, labels=labels)
for name, grp in df.groupby("band", observed=True):
    print(f"  {name:<6} {grp['error'].mean():+.2f} C   (n={len(grp)})")

print(f"\ncorrelation of error with forecast temp: {df['error'].corr(df['forecast_max']):+.2f}")

print("\n--- verdict rule agreed in advance ---")
print(f"|mean| = {abs(mean):.2f},  sd/2 = {sd / 2:.2f}")
print("PREMISE HOLDS" if abs(mean) > sd / 2 else "PREMISE WEAK on mean bias alone")
