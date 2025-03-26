
import pandas as pd

# Load logistic regression result (manually saved summary)
with open("eda_outputs/logistic_regression_summary.txt", "r") as f:
    summary_text = f.read()

print("=== LOGISTIC REGRESSION SUMMARY ===\n")
print(summary_text)

# Display interpretation notes
print("\n=== INTERPRETATION NOTES ===")
print("1. Stars/Forks are negatively associated with PR acceptance.")
print("2. Dependency PRs have the highest positive impact.")
print("3. Documentation and Feature PRs have mixed effects depending on repo size.")
print("4. Bug Fix PRs show modest positive effect, but not always statistically significant.")
