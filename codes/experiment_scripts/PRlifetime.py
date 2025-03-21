import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('combined_pr_data.csv')

# Parse datetime columns
df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
df['closed_at'] = pd.to_datetime(df['closed_at'], errors='coerce')
df['merged_at'] = pd.to_datetime(df['merged_at'], errors='coerce')

# Calculate PR lifetime
df['pr_lifetime'] = (df['closed_at'] - df['created_at']).dt.days
df = df.dropna(subset=['pr_lifetime'])
df['pr_lifetime'] = df['pr_lifetime'].astype(int)

# Define if the PR was merged
df['was_merged'] = df['merged_at'].notnull().astype(int)

# Define bins in days (based on years)
bins = [0, 365, 365*2, 365*3, 365*4, float('inf')]

# Define corresponding labels
labels = ['0-1 year', '1-2 years', '2-3 years', '3-4 years', '4+ years']

df['lifetime_group'] = pd.cut(df['pr_lifetime'], bins=bins, labels=labels, right=True, include_lowest=True)

# Group by custom lifetime bins
grouped = df.groupby('lifetime_group').agg(
    total_prs=('was_merged', 'count'),
    merged_prs=('was_merged', 'sum')
)
grouped['acceptance_rate'] = grouped['merged_prs'] / grouped['total_prs']

# Plotting
plt.figure(figsize=(10, 6))
plt.bar(grouped.index.astype(str), grouped['acceptance_rate'], color='skyblue')
plt.title('PR Acceptance Rate by PR Lifetime Group')
plt.xlabel('PR Lifetime (Days)')
plt.ylabel('Acceptance Rate')
plt.ylim(0, 1.05)
plt.grid(axis='y')
plt.tight_layout()
plt.show()
