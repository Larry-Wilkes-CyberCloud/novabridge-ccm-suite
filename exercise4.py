import pandas as pd
from itertools import combinations

invoices = pd.read_csv("data/invoices.csv")
invoices["invoice_date"] = pd.to_datetime(invoices["invoice_date"])

THRESHOLD = 5000

flags = []
for (vendor, date), group in invoices.groupby(["vendor_id", "invoice_date"]):
    if len(group) < 2:
        continue
    under = group[group["amount"] < THRESHOLD]
    if len(under) < 2:
        continue
    for combo in combinations(under.index, 2):
        pair = under.loc[list(combo)]
        if pair["amount"].sum() >= THRESHOLD:
            flags.append(pair)

if flags:
    flagged_df = pd.concat(flags).drop_duplicates()
    print(f"Potential split purchases: {len(flagged_df)} invoice rows")
    print(flagged_df[["invoice_id", "vendor_name", "amount", "invoice_date", "approved_by"]])
else:
    print("No potential split purchases found")
