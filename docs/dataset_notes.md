# Dataset Notes

The raw Crowpeaks CSV is treated as a customer-message dataset, not a business knowledge base.

Expected raw file:

```text
data/raw/Crowpeaks - label test data - 6K Sample.csv
```

Expected columns:

- `Input`: customer message used as the evaluation query
- `Output`: intent label such as Inquiry, Complaint, Support, Lead, Follow Up, or Other

If the raw CSV is not present, `experiments/prepare_eval_queries.py` exits with a clear error and does not create a misleading processed dataset.

Business knowledge lives separately in Markdown files under `data/business_docs/`.
