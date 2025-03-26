
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load cleaned dataset (assumes it's preprocessed and available as CSV)
df = pd.read_csv('cleaned_dataset.csv')

# Select relevant columns
cols = ["Stars", "Forks", "Bug Fix", "Feature", "Documentation", "Dependencies", "Accepted"]
corr_matrix = df[cols].corr()

# Plot heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Correlation Matrix: Repository Size, Labels, and PR Acceptance")
plt.tight_layout()
plt.savefig("correlation_heatmap.png")
plt.show()
