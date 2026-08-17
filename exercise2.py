import datetime
import pandas as pd

employees = pd.read_csv("data/employees.csv")
iam = pd.read_csv("data/iam_accounts.csv")

merged = employees.merge(iam, on="employee_id")

today = pd.Timestamp(datetime.date(2026, 8, 17))
merged["termination_date"] = pd.to_datetime(merged["termination_date"])
bad_dates = merged[merged["termination_date"] > today]
print(f"Data quality issue: {len(bad_dates)} termination date(s) in the future")

leavers_with_access = merged[
    (merged["status"] == "Terminated") &
    (merged["account_status"] == "Active") &
    (merged["termination_date"] <= today)
].copy()

print(f"Terminated employees with active accounts: {len(leavers_with_access)}")
print(leavers_with_access[["employee_id", "name", "termination_date", "account_status"]])

# Days of unremediated exposure — how long has this access sat open?
leavers_with_access["days_exposed"] = (today - leavers_with_access["termination_date"]).dt.days

# A simple remediation priority: longer exposure = higher priority.
# (In a real audit, you'd also weight by the employee's access level/department risk,
#  but we don't have that granularity here, so exposure time is the primary driver.)
leavers_with_access = leavers_with_access.sort_values("days_exposed", ascending=False)

print()
print(leavers_with_access[["employee_id", "name", "department", "termination_date", "days_exposed"]].to_string(index=False))
print()
print(f"Oldest unremediated leaver-access finding: {leavers_with_access.iloc[0]['name']}, "
      f"{leavers_with_access.iloc[0]['days_exposed']} days of exposure since termination")

dept_risk_weight = {
    "IT": 3, "Finance": 3, "Procurement": 2,
    "HR": 2, "Sales": 1, "Warehouse": 1
}

leavers_with_access["dept_risk"] = leavers_with_access["department"].map(dept_risk_weight)
leavers_with_access["remediation_score"] = leavers_with_access["days_exposed"] * leavers_with_access["dept_risk"]

print()
print(leavers_with_access.sort_values("remediation_score", ascending=False)[
    ["employee_id", "name", "department", "days_exposed", "dept_risk", "remediation_score"]
].to_string(index=False))
