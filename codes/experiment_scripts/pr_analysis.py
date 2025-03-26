
import os
import pandas as pd
import numpy as np
import zipfile
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

# === 1. Load and Clean Data ===
zip_path = "dataset.zip"
extract_dir = "extracted_dataset"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

dataset_path = os.path.join(extract_dir, "dataset")
repo_folders = os.listdir(dataset_path)

all_prs = []
for repo in repo_folders:
    repo_path = os.path.join(dataset_path, repo)
    pr_files = [f for f in os.listdir(repo_path) if f.endswith("-prs.csv")]
    if pr_files:
        df = pd.read_csv(os.path.join(repo_path, pr_files[0]))
        df["repository"] = repo
        all_prs.append(df)

df = pd.concat(all_prs, ignore_index=True)

# Parse datetime and size columns
df["Created At"] = pd.to_datetime(df["Created At"], errors="coerce")
df["Merged At"] = pd.to_datetime(df["Merged At"], errors="coerce")
df["Closed At"] = pd.to_datetime(df["Closed At"], errors="coerce")
df[["Stars", "Forks", "Contributors", "Commits"]] = df["Repository Size (Stars, Forks, Contributors, Commits)"].str.split(", ", expand=True)
for col in ["Stars", "Forks", "Contributors", "Commits"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df["Accepted"] = df["Merged At"].notna().astype(int)
df["Labels"] = df["Labels"].fillna("")

# Extract labels
label_keywords = {
    "Bug Fix": ["bug", "fix"],
    "Feature": ["feature", "enhancement"],
    "Documentation": ["docs", "documentation"],
    "Dependencies": ["dependencies", "dependabot"]
}
for label, keywords in label_keywords.items():
    df[label] = df["Labels"].apply(lambda x: any(kw in x.lower() for kw in keywords)).astype(int)

# === 2. EDA ===
eda_dir = "eda_outputs"
os.makedirs(eda_dir, exist_ok=True)

# Histogram: Stars and Forks
plt.hist(df["Stars"].dropna(), bins=20, edgecolor='black')
plt.title("Distribution of Stars")
plt.xlabel("Stars")
plt.ylabel("Frequency")
plt.savefig(f"{eda_dir}/stars_distribution.png")
plt.clf()

plt.hist(df["Forks"].dropna(), bins=20, edgecolor='black', color='orange')
plt.title("Distribution of Forks")
plt.xlabel("Forks")
plt.ylabel("Frequency")
plt.savefig(f"{eda_dir}/forks_distribution.png")
plt.clf()

# PR acceptance rate per repository
repo_acceptance = df.groupby("repository")["Accepted"].mean().sort_values(ascending=False) * 100
repo_acceptance.to_csv(f"{eda_dir}/acceptance_by_repo.csv")

# === 3. Correlation ===
corr_matrix = df[["Stars", "Forks", "Bug Fix", "Feature", "Documentation", "Dependencies", "Accepted"]].corr()
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Matrix")
plt.savefig(f"{eda_dir}/correlation_heatmap.png")
plt.clf()

# === 4. Logistic Regression ===
features = ["Stars", "Forks", "Bug Fix", "Feature", "Documentation", "Dependencies"]
X = df[features].fillna(0)
X = sm.add_constant(X)
y = df["Accepted"]
logit_model = sm.Logit(y, X)
result = logit_model.fit()

# Save regression summary to file
with open(f"{eda_dir}/logistic_regression_summary.txt", "w") as f:
    f.write(result.summary().as_text())

# Plot coefficients
coefs = result.params[1:]
plt.barh(coefs.index, coefs.values, color=["green" if c > 0 else "red" for c in coefs.values])
plt.axvline(0, color="black", linestyle="--")
plt.title("Logistic Regression Coefficients")
plt.xlabel("Coefficient")
plt.tight_layout()
plt.savefig(f"{eda_dir}/logistic_coefficients.png")
