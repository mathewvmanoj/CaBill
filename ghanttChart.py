import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from datetime import datetime

# Project Tasks Data
# Each task contains planned and actual dates with customizable colors

data = {
    "Task": ["Phase 1", "Phase 2", "Phase 2 - Subtask 1", "Phase 2 - Subtask 2", "Phase 3", "Phase 4"],
    "Planned_Start": ["2025-01-20", "2025-02-05", "2025-02-13", "2025-02-27", "2025-03-03", "2025-03-17"],
    "Planned_End": ["2025-02-05", "2025-02-12", "2025-02-26", "2025-03-05", "2025-03-16", "2025-03-30"],
    "Actual_Start": ["2025-01-20", "2025-02-05", "2025-02-13", "2025-02-20", "2025-03-05", None],
    "Actual_End": ["2025-02-05", "2025-02-12", "2025-02-28", "2025-02-28", None, None],
    "Description": [
        "Requirement Gathering, \nProject Planning & Designing",
        "Login, Auth, Lantiv Development, \nChatbot - POC",
        "Timesheet & Major feature Development \nChatbot Initial Implementation",
        "Deployment Env setup",
        "Frontend-Backend Integration, \nChatbot Testing",
        "System Testing & \nDeployment in VM Systems"
    ]
}

# Convert dates to datetime format
df = pd.DataFrame(data)
df["Planned_Start"] = pd.to_datetime(df["Planned_Start"])
df["Planned_End"] = pd.to_datetime(df["Planned_End"])
df["Actual_Start"] = pd.to_datetime(df["Actual_Start"])
df["Actual_End"] = pd.to_datetime(df["Actual_End"])

# Color Configuration
planned_color = "#FFC107"  # Yellow
actual_color = "#4CAF50"   # Green

# Plotting the Gantt Chart
fig, ax = plt.subplots(figsize=(14, 8))
used_labels = set()

for i, row in df.iterrows():
    # Plot Planned Task
    ax.barh(i + 0.2, (row["Planned_End"] - row["Planned_Start"]).days, left=row["Planned_Start"],
            color=planned_color, height=0.4, label="Planned" if "Planned" not in used_labels else "")
    used_labels.add("Planned")
    ax.text(row["Planned_Start"] + (row["Planned_End"] - row["Planned_Start"]) / 2, i + 0.2, row["Description"],
            va='center', ha='center', fontsize=10, color='black')

    # Plot Actual Task if available
    if pd.notna(row["Actual_Start"]) and pd.notna(row["Actual_End"]):
        ax.barh(i - 0.2, (row["Actual_End"] - row["Actual_Start"]).days, left=row["Actual_Start"],
                color=actual_color, height=0.4, edgecolor="black", label="Actual" if "Actual" not in used_labels else "")
        used_labels.add("Actual")
        ax.text(row["Actual_Start"] + (row["Actual_End"] - row["Actual_Start"]) / 2, i - 0.2, "Actual Progress",
                va='center', ha='center', fontsize=10, color='blue')

# Date Formatting
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
plt.xticks(rotation=45)

# Titles and Labels
plt.title("Project Gantt Chart with Planned vs Actual Progress")
plt.xlabel("Timeline")
plt.ylabel("Project Tasks")
plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
plt.legend(title="Progress Type", loc='upper left')
plt.tight_layout()

plt.show()
