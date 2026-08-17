import pandas as pd

je = pd.read_csv("data/journal_entries.csv")
je["posted_at"] = pd.to_datetime(je["posted_at"])

je["weekday"] = je["posted_at"].dt.dayofweek  # 5=Sat, 6=Sun
je["hour"] = je["posted_at"].dt.hour

is_weekend = je["weekday"] >= 5
is_after_hours = (je["hour"] < 6) | (je["hour"] >= 20)

flagged = je[is_weekend | is_after_hours]

print(f"Total journal entries: {len(je)}")
print(f"Flagged as weekend/after-hours: {len(flagged)} ({len(flagged)/len(je)*100:.1f}%)")
print()
print(flagged[["je_id", "posted_by", "posted_at", "amount", "account"]].sort_values("posted_at"))
print()
print(f"Total dollar magnitude (abs) of flagged entries: ${flagged['amount'].abs().sum():,.2f}")
