# FictiPay Datathon — Churn Prediction Dataset

## Context
FictiPay is a mobile wallet platform in Emergingland serving millions of
retail, merchant, and biller accounts. Your task is to predict which
customers will become **inactive within the next 30 days**.

## Churn Definition
A customer is labelled **CHURN = 1** if they made **no transaction between
2024-04-01 and 2024-04-30** (the 30-day prediction window).
A customer is labelled **CHURN = 0** if they made at least one transaction
in that period.

Features must be built **exclusively** from the observation window
(2024-01-01 → 2024-03-31). The prediction window data is not provided.

## Files

| File | Rows | Description |
|---|---|---|
| `kyc.parquet` | ~2 M | Account metadata (all account types) |
| `transactions/trx_2024-0[1-3].parquet` | ~200 M total | Transactions — observation period only |
| `dayend_balance/balance_2024-0[1-3].parquet` | ~360 M total | Daily balances — observation period only |
| `train_labels.csv` | 595,000 | Customer IDs + CHURN label (training set) |
| `test.csv` | 255,000 | Customer IDs to predict (no label) |
| `sample_submission.csv` | 255,000 | Expected submission format |

## Table Schemas

**KYC** — `ACCOUNT_ID · ACCOUNT_TYPE · ACCOUNT_OPEN_DATE · GENDER · REGION`
- ACCOUNT_TYPE: Customer / Merchant / Biller
- Only Customer accounts appear in train_labels.csv and test.csv

**Transaction** — `TrxID · TRX_DATETIME · SRC_ACCOUNT · DST_ACCOUNT · TRX_TYPE · TRX_AMT`
- TRX_TYPE: P2P / MerchantPay / BillPay / CashIn / CashOut

**DayEndBalance** — `ACCOUNT_ID · DATE · AVAILABLE_BALANCE`

## Label Distribution (training set)

| Label | Count | Rate |
|---|---|---|
| CHURN = 1 | 75,435 | 12.7% |
| CHURN = 0 | 519,565 | 87.3% |

## Submission Format
Submit a CSV with exactly two columns for every row in `test.csv`:

```
ACCOUNT_ID,CHURN_PROB
CUST000000000001,0.823
CUST000000000002,0.041
...
```

`CHURN_PROB` must be a float in [0, 1]. Submissions are evaluated using
**AUC-ROC** against the private ground truth.

## Important Notes
- The transaction and balance tables are too large for in-memory pandas.
  Use **Dask** or **PySpark** for processing.
- Merchants and Billers appear in transaction DST_ACCOUNT columns but
  are **not** in the prediction target — focus on Customer accounts only.
- Feature engineering is the core of this challenge. A raw feature count,
  distribution analysis, and business justification are all evaluated.
