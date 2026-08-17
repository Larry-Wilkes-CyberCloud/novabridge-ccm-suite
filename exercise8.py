import pandas as pd

# Recompute each finding count/magnitude from earlier exercises
employees = pd.read_csv("data/employees.csv")
iam = pd.read_csv("data/iam_accounts.csv")
invoices = pd.read_csv("data/invoices.csv")
je = pd.read_csv("data/journal_entries.csv")
access = pd.read_csv("data/access_rights.csv")
gl = pd.read_csv("data/gl_balances.csv")
subledger = pd.read_csv("data/ap_subledger.csv")

findings = []

# Leaver access (Exercise 2 logic, simplified)
merged = employees.merge(iam, on="employee_id")
merged["termination_date"] = pd.to_datetime(merged["termination_date"])
today = pd.Timestamp("2026-08-17")
leavers = merged[(merged["status"]=="Terminated") & (merged["account_status"]=="Active") & (merged["termination_date"]<=today)]
findings.append({"control": "Leaver Access Review", "population": len(employees), "exceptions": len(leavers), "dollar_impact": None})

# SoD conflicts (Exercise 6)
conflicts = access[(access["can_approve_po"]==True) & (access["can_create_vendor"]==True)]
findings.append({"control": "Segregation of Duties", "population": len(access), "exceptions": len(conflicts), "dollar_impact": None})

# GL reconciliation breaks (Exercise 7)
subledger_totals = subledger.groupby("month")["amount"].sum().reset_index()
subledger_totals.columns = ["month", "subledger_total"]
recon = gl.merge(subledger_totals, on="month")
recon["variance"] = recon["gl_balance"] - recon["subledger_total"]
breaks = recon[recon["variance"].abs() > 0.01]
findings.append({"control": "GL Reconciliation", "population": len(gl), "exceptions": len(breaks), "dollar_impact": breaks["variance"].abs().sum()})

summary = pd.DataFrame(findings)
summary["exception_rate"] = (summary["exceptions"] / summary["population"] * 100).round(1)

print(summary.to_string(index=False))
print()
print("Prioritized by exception rate (highest risk first):")
print(summary.sort_values("exception_rate", ascending=False)[["control", "exception_rate", "exceptions"]].to_string(index=False))

# Only compute dollar_score for controls that actually have a dollar figure.
# Controls without one are scored on rate alone — never defaulted to 0,
# which would silently understate their real risk.
has_dollar = summary["dollar_impact"].notna()

summary["rate_score"] = (summary["exception_rate"] / summary["exception_rate"].max() * 100).round(1)

summary["priority_score"] = None
summary.loc[has_dollar, "dollar_score"] = (summary.loc[has_dollar, "dollar_impact"] / summary.loc[has_dollar, "dollar_impact"].max() * 100).round(1)
summary.loc[has_dollar, "priority_score"] = (summary.loc[has_dollar, "rate_score"] * 0.4 + summary.loc[has_dollar, "dollar_score"] * 0.6).round(1)
summary.loc[~has_dollar, "priority_score"] = summary.loc[~has_dollar, "rate_score"]

print()
print("Prioritized by combined priority score:")
print(summary.sort_values("priority_score", ascending=False)[["control", "exception_rate", "dollar_impact", "priority_score"]].to_string(index=False))
print()
print("Note: controls without a quantified dollar impact (SoD, Leaver Access) are scored on")
print("exception rate alone, not blended with an assumed-zero dollar figure — a 0 would")
print("understate their real risk rather than honestly reflect 'unmeasured.'")
