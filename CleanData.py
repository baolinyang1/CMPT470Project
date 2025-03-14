import os
import pandas as pd
import numpy as np

# Define the root folder where all datasets are stored
DATA_FOLDER = r"C:\Users\YuvrajKorotana\PycharmProjects\pythonProject3\dataset"

# List all project folders (each folder represents one dataset, e.g., Angular, Pytorch, Nodejs)
project_folders = [f for f in os.listdir(DATA_FOLDER) if os.path.isdir(os.path.join(DATA_FOLDER, f))]

# Create empty lists to store data
all_contributors = []
all_prs = []
all_comments = []

# Function to load CSV files for each project
def load_project_data(project_name):
    project_path = os.path.join(DATA_FOLDER, project_name)

    # Define expected filenames
    contributors_file = f"{project_name}-{project_name}-contributors.csv"
    prs_file = f"{project_name}-{project_name}-prs.csv"
    comments_file = f"{project_name}-{project_name}-comments.csv"

    # Read Contributors Data
    if os.path.exists(os.path.join(project_path, contributors_file)):
        df_contributors = pd.read_csv(os.path.join(project_path, contributors_file))
        df_contributors["source_project"] = project_name  # Tag with project name
        all_contributors.append(df_contributors)

    # Read Pull Requests (PR) Data
    if os.path.exists(os.path.join(project_path, prs_file)):
        df_prs = pd.read_csv(os.path.join(project_path, prs_file))
        df_prs["source_project"] = project_name  # Tag with project name
        all_prs.append(df_prs)

    # Read Comments Data
    if os.path.exists(os.path.join(project_path, comments_file)):
        df_comments = pd.read_csv(os.path.join(project_path, comments_file))
        df_comments["source_project"] = project_name  # Tag with project name
        all_comments.append(df_comments)

# Process all project folders
for project in project_folders:
    load_project_data(project)

# Combine datasets into unified DataFrames
df_contributors = pd.concat(all_contributors, ignore_index=True)
df_prs = pd.concat(all_prs, ignore_index=True)
df_comments = pd.concat(all_comments, ignore_index=True)

# Standardize Column Names (Lowercase, Remove Spaces)
for df in [df_contributors, df_prs, df_comments]:
    df.columns = df.columns.str.lower().str.replace(" ", "_")

# Drop Duplicates
df_contributors.drop_duplicates(inplace=True)
df_prs.drop_duplicates(inplace=True)
df_comments.drop_duplicates(inplace=True)

# Convert Dates to Datetime Format
date_cols = ["created_at", "merged_at", "closed_at"]
for col in date_cols:
    if col in df_prs.columns:
        df_prs[col] = pd.to_datetime(df_prs[col], errors="coerce")

# Filter Out Bots (Only for Contributors Dataset)
if "type" in df_contributors.columns:
    df_contributors = df_contributors[df_contributors["type"].str.lower() != "bot"]

# Handle Missing Values
df_prs.fillna({"review_comments": 0, "comments": 0, "lines_added": 0, "lines_deleted": 0}, inplace=True)
df_prs.dropna(subset=["pr_id", "pr_author"], inplace=True)  # Ensure essential fields exist

# Convert all relevant numeric columns to proper numeric types
numeric_cols = ["total_prs_merged", "total_prs_submitted", "account_age_(days)"]
for col in numeric_cols:
    if col in df_contributors.columns:
        df_contributors[col] = pd.to_numeric(df_contributors[col], errors="coerce")  # Convert strings to numbers

# Ensure no division by zero when computing approval rate
df_contributors["approval_rate"] = np.where(
    df_contributors["total_prs_submitted"] == 0,
    0,  # Set approval rate to 0 if no PRs were submitted
    df_contributors["total_prs_merged"] / df_contributors["total_prs_submitted"]
)

# Fix Chained Assignment Warning
df_contributors["approval_rate"] = df_contributors["approval_rate"].fillna(0)

# Compute Contributor Seniority (Convert account age from days to years)
if "account_age_(days)" in df_contributors.columns:
    df_contributors["contributor_seniority"] = (df_contributors["account_age_(days)"] / 365).round(2)

# Fix Chained Assignment Warning
df_contributors["contributor_seniority"] = df_contributors["contributor_seniority"].fillna(0)

# Compute Average Review Comments per PR
if "review_comments" in df_prs.columns and "total_prs_submitted" in df_contributors.columns:
    df_prs["avg_review_comments"] = df_prs["review_comments"] / df_contributors["total_prs_submitted"]
    df_prs["avg_review_comments"] = df_prs["avg_review_comments"].fillna(0)  # Avoid NaN values

# Save Cleaned Data
output_folder = os.path.join(DATA_FOLDER, "cleaned_data")
os.makedirs(output_folder, exist_ok=True)

df_contributors.to_csv(os.path.join(output_folder, "cleaned_contributors.csv"), index=False)
df_prs.to_csv(os.path.join(output_folder, "cleaned_prs.csv"), index=False)
df_comments.to_csv(os.path.join(output_folder, "cleaned_comments.csv"), index=False)

# Display Sample Outputs
print("Contributors Data Sample:")
print(df_contributors.head())

print("\nPR Data Sample:")
print(df_prs.head())

print("\nComments Data Sample:")
print(df_comments.head())
