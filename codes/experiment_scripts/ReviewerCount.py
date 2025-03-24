import pandas as pd
import matplotlib.pyplot as plt

PR_CSV_FILE = "combined_pr_data.csv"

def plotSuccessRateByReviewerCount(data: pd.DataFrame):
    bins = [0,1,2,4,8,30]
    labels = ['0', '1', "2-3", "4-7", ">7"]
    data["reviewer_count_group"] = pd.cut(data["reviewer_count"], bins=bins, labels=labels, right=False)
    averageAcceptanceRates = data.groupby("reviewer_count_group")["accepted"].mean() * 100

    # Graph Formatting
    plt.figure(figsize=(8,5))
    plt.bar(averageAcceptanceRates.index, averageAcceptanceRates.values, color='lightblue', edgecolor='black')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=0)
    plt.ylim(0,100)
    plt.xlabel("Reviewer Count")
    plt.ylabel("Acceptance Rate (%)")

    plt.savefig('./ReviewerCount_AcceptanceRate.png', bbox_inches='tight')


if __name__ == "__main__":
    # Read csv file
    prs = pd.read_csv(PR_CSV_FILE)

    # Remove prs that are not closed yet
    prs = prs.dropna(subset=["closed_at"]) 

    # Add column for the number of reviewers
    def count_reviewers(row):
        if pd.isna(row["reviewers"]):
            return 0 
        
        return len(row["reviewers"].split(","))

    prs["reviewer_count"] = prs.apply(count_reviewers, axis=1)

    # Add boolean column for if the pr was accepted or not (has merged_at date)
    prs['accepted'] = ~prs["merged_at"].isna()

    plotSuccessRateByReviewerCount(prs)
