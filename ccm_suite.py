import pandas as pd
import numpy as np
from datetime import datetime

TODAY = pd.Timestamp("2026-08-17")

def load_data():
    return {
        "employees": pd.read_csv("data/employees.csv"),
        "iam": pd.read_csv("data/iam_accounts.csv"),
        "vendors": pd.read_csv("data/vendors.csv"),
        "invoices": pd.read_csv("data/invoices.csv"),
        "je": pd.read_csv("data/journal_entries.csv"),
        "access": pd.read_csv("data/access_rights.csv"),
        "gl": pd.read_csv("data/gl_balances.csv"),
        "subledger": pd.read_csv("data/ap_subledger.csv"),
    }

def check_leaver_access(data):
    merged = data["employees"].merge(data["iam"], on="employee_id")
    merged["termination_date"] = pd.to_datetime(merged["termination_date"])
    leavers = merged[
        (merged["status"] == "Terminated") &
        (merged["account_status"] == "Active") &
        (merged["termination_date"] <= TODAY)
    ].copy()
    leavers["days_exposed"] = (TODAY - leavers["termination_date"]).dt.days
    dept_risk = {"IT": 3, "Finance": 3, "Procurement": 2, "HR": 2, "Sales": 1, "Warehouse": 1}
    leavers["dept_risk"] = leavers["department"].map(dept_risk)
    leavers["remediation_score"] = leavers["days_exposed"] * leavers["dept_risk"]
    return {
        "control": "Leaver Access Review", "population": len(data["employees"]),
        "exceptions": len(leavers), "dollar_impact": None, "detail": leavers
    }

def check_sod_conflicts(data):
    access = data["access"]
    conflicts = access[(access["can_approve_po"] == True) & (access["can_create_vendor"] == True)]
    return {
        "control": "Segregation of Duties", "population": len(access),
        "exceptions": len(conflicts), "dollar_impact": None, "detail": conflicts
    }

def check_gl_reconciliation(data):
    subledger_totals = data["subledger"].groupby("month")["amount"].sum().reset_index()
    subledger_totals.columns = ["month", "subledger_total"]
    recon = data["gl"].merge(subledger_totals, on="month")
    recon["variance"] = recon["gl_balance"] - recon["subledger_total"]
    breaks = recon[recon["variance"].abs() > 0.01]
    return {
        "control": "GL Reconciliation", "population": len(data["gl"]),
        "exceptions": len(breaks), "dollar_impact": breaks["variance"].abs().sum() if len(breaks) else None,
        "detail": breaks
    }

def check_duplicate_payments(data):
    invoices = data["invoices"].copy()
    invoices["invoice_date"] = pd.to_datetime(invoices["invoice_date"])
    invoices_sorted = invoices.sort_values(["vendor_id", "amount", "invoice_date"])
    duplicates = []
    for (vendor, amount), group in invoices_sorted.groupby(["vendor_id", "amount"]):
        if len(group) > 1:
            dates = group["invoice_date"].tolist()
            for i in range(len(dates) - 1):
                if (dates[i+1] - dates[i]).days <= 7:
                    duplicates.append(group.iloc[[i, i+1]])
    detail = pd.concat(duplicates).drop_duplicates() if duplicates else pd.DataFrame()
    return {
        "control": "Duplicate Payments", "population": len(invoices),
        "exceptions": len(detail), "dollar_impact": detail["amount"].sum() if len(detail) else None,
        "detail": detail
    }

def check_split_purchases(data, threshold=5000):
    from itertools import combinations
    invoices = data["invoices"].copy()
    invoices["invoice_date"] = pd.to_datetime(invoices["invoice_date"])
    flags = []
    for (vendor, date), group in invoices.groupby(["vendor_id", "invoice_date"]):
        under = group[group["amount"] < threshold]
        if len(under) < 2:
            continue
        for combo in combinations(under.index, 2):
            pair = under.loc[list(combo)]
            if pair["amount"].sum() >= threshold:
                flags.append(pair)
    detail = pd.concat(flags).drop_duplicates() if flags else pd.DataFrame()
    return {
        "control": "Split Purchases", "population": len(invoices),
        "exceptions": len(detail), "dollar_impact": detail["amount"].sum() if len(detail) else None,
        "detail": detail
    }

def check_after_hours_je(data):
    je = data["je"].copy()
    je["posted_at"] = pd.to_datetime(je["posted_at"])
    is_weekend = je["posted_at"].dt.dayofweek >= 5
    is_after_hours = (je["posted_at"].dt.hour < 6) | (je["posted_at"].dt.hour >= 20)
    detail = je[is_weekend | is_after_hours]
    return {
        "control": "After-Hours Journal Entries", "population": len(je),
        "exceptions": len(detail), "dollar_impact": detail["amount"].abs().sum() if len(detail) else None,
        "detail": detail
    }

def build_report(results):
    summary_rows = []
    for r in results:
        pop = r["population"]
        exc = r["exceptions"]
        rate = round(exc / pop * 100, 1) if pop else 0
        summary_rows.append({
            "control": r["control"], "population": pop, "exceptions": exc,
            "exception_rate": rate, "dollar_impact": r["dollar_impact"]
        })
    summary = pd.DataFrame(summary_rows)

    has_dollar = summary["dollar_impact"].notna()
    summary["rate_score"] = (summary["exception_rate"] / summary["exception_rate"].max() * 100).round(1)
    summary.loc[has_dollar, "dollar_score"] = (
        summary.loc[has_dollar, "dollar_impact"] / summary.loc[has_dollar, "dollar_impact"].max() * 100
    ).round(1)
    summary.loc[has_dollar, "priority_score"] = (
        summary.loc[has_dollar, "rate_score"] * 0.4 + summary.loc[has_dollar, "dollar_score"] * 0.6
    ).round(1)
    summary.loc[~has_dollar, "priority_score"] = summary.loc[~has_dollar, "rate_score"]

    return summary.sort_values("priority_score", ascending=False)

if __name__ == "__main__":
    data = load_data()
    results = [
        check_leaver_access(data), check_sod_conflicts(data), check_gl_reconciliation(data),
        check_duplicate_payments(data), check_split_purchases(data), check_after_hours_je(data),
    ]

    print("=" * 70)
    print("CONTINUOUS CONTROLS MONITORING SUITE - FINDINGS REPORT")
    print("=" * 70)
    report = build_report(results)
    print(report[["control", "exceptions", "exception_rate", "dollar_impact", "priority_score"]].to_string(index=False))
    print()
    print(f"Total exceptions across all controls: {sum(r['exceptions'] for r in results)}")
    total_dollars = sum(r["dollar_impact"] for r in results if r["dollar_impact"] is not None)
    print(f"Total quantified dollar exposure: ${total_dollars:,.2f}")
