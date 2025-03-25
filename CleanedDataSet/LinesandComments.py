import matplotlib.pyplot as plt
import pandas as pd

# Load the Data
file_path = "all_pr.csv"  # Ensure this file is in the same directory

df = pd.read_csv(file_path)

# Define bins (categories) for lines added
bins_added = [0, 100, 500, 1000, 5000, df["lines_added"].max()]
labels_added = ["0-100", "101-500", "501-1000", "1001-5000", "5001+"]

df["lines_added_category"] = pd.cut(df["lines_added"], bins=bins_added, labels=labels_added, right=True)

# Calculate acceptance rate for each category
acceptance_rates_added = df.groupby("lines_added_category")["accepted"].mean() * 100

# Plot the Bar Chart
plt.figure(figsize=(8,5))
plt.bar(acceptance_rates_added.index, acceptance_rates_added.values, color='lightblue', edgecolor='black')
plt.xlabel("Lines Added Category")
plt.ylabel("Acceptance Rate (%)")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()
