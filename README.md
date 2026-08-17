# NovaBridge CCM Suite

A self-directed Python/pandas Continuous Controls Monitoring (CAAT) practice project, built against a synthetic ERP/HR dataset with realistic seeded audit findings.

## What this does

The suite runs six independent controls, each modeled after a real audit test:

- **Leaver Access Review** — terminated employees whose IAM accounts are still active, prioritized by days of exposure and department risk
- **Duplicate Payment Detection** — same vendor, same amount, invoices posted within a week of each other
- **Split Purchase Detection** — same vendor, same day, multiple sub-threshold invoices whose combined total crosses the approval threshold
- **After-Hours/Weekend Journal Entry Detection** — journal entries posted outside business hours or on weekends
- **Segregation of Duties Conflict Modeling** — employees with both purchase-order approval and vendor-creation access
- **GL-to-Subledger Reconciliation** — monthly GL balances compared against AP subledger totals, flagging variances beyond a rounding tolerance

## Results

Across all six controls: **113 total exceptions**, **$1,447,898.34** in total quantified dollar exposure.

Findings are ranked with a composite priority-scoring methodology that blends exception rate and dollar impact (weighted 40%/60%) into a single 0–100 score, so controls can be compared on a common scale even when only some of them produce a dollar figure. Controls without a quantified dollar impact are scored on exception rate alone rather than defaulted to a zero dollar score, which would otherwise understate their risk.

## How to run it

```
python ccm_suite.py
```

Run from the project root. Requires the `data/` folder with the CSVs, and `pandas`/`numpy` installed.

## What I learned

Most of the real value here came from catching bugs in the detection logic itself, not from the findings — a threshold-check bug that undercounted split purchases, a synthetic-data generation flaw that inflated one exception rate to an implausible 33%, and a scoring bug that silently capped non-dollar-based findings. None of these were obvious from the output alone; each one only surfaced by questioning whether a result made sense before trusting it at face value.
