import pandas as pd

subledger = pd.read_csv("data/ap_subledger.csv")
gl = pd.read_csv("data/gl_balances.csv")

subledger_totals = subledger.groupby("month")["amount"].sum().reset_index()
subledger_totals.columns = ["month", "subledger_total"]

recon = gl.merge(subledger_totals, on="month")
recon["variance"] = recon["gl_balance"] - recon["subledger_total"]
recon["is_broken"] = recon["variance"].abs() > 0.01  # allow for tiny float rounding

print(recon)
print()
breaks = recon[recon["is_broken"]]
print(f"Months with reconciliation breaks: {len(breaks)}")
print(breaks[["month", "gl_balance", "subledger_total", "variance"]])
