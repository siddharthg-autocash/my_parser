# import os
# import json
# import pandas as pd
# import numpy as np
# from rapidfuzz import fuzz, distance
# import matplotlib.pyplot as plt

# OUT_DIR = "benchmark_res"
# INPUT_FILE = "project_gamma/experiments/RM_INN_PSSI_TxnData_Oct-Dec25.csv"
# THRESHOLD = 50

# os.makedirs(OUT_DIR, exist_ok=True)

# df = pd.read_csv(INPUT_FILE)

# def norm(s):
#     if pd.isna(s):
#         return ""
#     return str(s).upper().strip()

# def resolve_amount(row):
#     if not pd.isna(row.get("transaction_amount")):
#         return float(row["transaction_amount"])
#     if not pd.isna(row.get("settlement_amount")):
#         return float(row["settlement_amount"])
#     return None

# # load ctpty fx
# from ..src.gamma.service.script import CTPTY

# def run_ctpty(row):
#     try:
#         final, fmt = CTPTY(row["narrative"], resolve_amount(row))
#         ctpty = final.get("ctpty", {})

#         return pd.Series({
#             "ctpty_payer": ctpty.get("payer"),
#             "ctpty_payee": ctpty.get("payee"),
#             "parse_result": json.dumps(final, ensure_ascii=False)
#         })
#     except Exception:
#         return pd.Series({
#             "ctpty_payer": None,
#             "ctpty_payee": None,
#             "parse_result": None
#         })

# df = pd.concat([df, df.apply(run_ctpty, axis=1)], axis=1)

# df["cpty_name_n"] = df["cpty_name"].apply(norm)

# df_gt = df[df["cpty_name_n"] != ""].copy()
# df_no_gt = df[df["cpty_name_n"] == ""].copy()

# def weighted_score(a, b):
#     if not a or not b:
#         return 0.0

#     jw = distance.JaroWinkler.similarity(a, b) * 100
#     ts = fuzz.token_set_ratio(a, b)
#     tso = fuzz.token_sort_ratio(a, b)

#     return (0.34 * jw) + (0.33 * ts) + (0.33 * tso)

# def benchmark_row(row):
#     payer_s = weighted_score(row["cpty_name_n"], norm(row["ctpty_payer"]))
#     payee_s = weighted_score(row["cpty_name_n"], norm(row["ctpty_payee"]))

#     best = max(payer_s, payee_s)

#     if best >= THRESHOLD:
#         return pd.Series({
#             "MATCHED": 1,
#             "MATCH_ROLE": "payer" if payer_s >= payee_s else "payee",
#             "BEST_SCORE": best
#         })
#     else:
#         return pd.Series({
#             "MATCHED": 0,
#             "MATCH_ROLE": "none",
#             "BEST_SCORE": best
#         })

# df_gt = pd.concat([df_gt, df_gt.apply(benchmark_row, axis=1)], axis=1)


# # plot
# plt.figure(figsize=(6, 4))
# counts = df_gt["MATCHED"].value_counts().sort_index()
# colors = ["#d62728", "#2ca02c"]  # red = fail, green = success

# bars = plt.bar(
#     ["Unmatched", "Matched"],
#     counts.values,
#     color=colors
# )

# total = counts.sum()
# for bar, val in zip(bars, counts.values):
#     plt.text(
#         bar.get_x() + bar.get_width() / 2,
#         bar.get_height(),
#         f"{(val/total)*100:.1f}%",
#         ha="center",
#         va="bottom",
#         fontsize=10
#     )

# plt.title("CTPTY Match Accuracy (Ground Truth)")
# plt.ylabel("Number of Transactions")
# plt.grid(axis="y", alpha=0.3)
# plt.savefig(f"{OUT_DIR}/match_accuracy.png", dpi=200, bbox_inches="tight")
# plt.close()


# To check:

import os
import json
import pandas as pd
from rapidfuzz import fuzz, distance
import matplotlib.pyplot as plt

OUT_DIR = "benchmark_res"
INPUT_FILE = "project_gamma/experiments/RM_INN_PSSI_TxnData_Oct-Dec25.csv"
THRESHOLD = 40
EXCEL_OUT = f"{OUT_DIR}/ctpty_benchmark.xlsx"

os.makedirs(OUT_DIR, exist_ok=True)

# Load data
df = pd.read_csv(INPUT_FILE)

def norm(s):
    if pd.isna(s):
        return ""
    return str(s).upper().strip()

def resolve_amount(row):
    if not pd.isna(row.get("transaction_amount")):
        return float(row["transaction_amount"])
    if not pd.isna(row.get("settlement_amount")):
        return float(row["settlement_amount"])
    return None

# Load CTPTY
from ..src.gamma.service.script import CTPTY

def run_ctpty(row):
    try:
        final, fmt = CTPTY(row["narrative"], resolve_amount(row))
        ctpty = final.get("ctpty", {})

        return pd.Series({
            "ctpty_counterparty": ctpty.get("counterparty"),
            "parse_result": json.dumps(final, ensure_ascii=False)
        })
    except Exception:
        return pd.Series({
            "ctpty_counterparty": None,
            "parse_result": None
        })

df = pd.concat([df, df.apply(run_ctpty, axis=1)], axis=1)

# Normalize names
df["cpty_name_n"] = df["cpty_name"].apply(norm)
df["ctpty_counterparty_n"] = df["ctpty_counterparty"].apply(norm)

# Split Ground Truth availability
df_gt = df[df["cpty_name_n"] != ""].copy()
df_no_gt = df[df["cpty_name_n"] == ""].copy()

# Matching logic 
def weighted_score(a, b):
    if not a or not b:
        return 0.0

    jw = distance.JaroWinkler.similarity(a, b) * 100
    ts = fuzz.token_set_ratio(a, b)
    tso = fuzz.token_sort_ratio(a, b)

    return (0.34 * jw) + (0.33 * ts) + (0.33 * tso)

def benchmark_row(row):
    score = weighted_score(
        row["cpty_name_n"],
        row["ctpty_counterparty_n"]
    )

    return pd.Series({
        "MATCHED": int(score >= THRESHOLD),
        "BEST_SCORE": round(score, 2)
    })

df_gt = pd.concat([df_gt, df_gt.apply(benchmark_row, axis=1)], axis=1)

df_matched = df_gt[df_gt["MATCHED"] == 1].copy()
df_unmatched = df_gt[df_gt["MATCHED"] == 0].copy()

with pd.ExcelWriter(EXCEL_OUT, engine="openpyxl") as writer:
    df_matched.to_excel(writer, sheet_name="matched", index=False)
    df_unmatched.to_excel(writer, sheet_name="unmatched", index=False)
    df_no_gt.to_excel(writer, sheet_name="Unavailable_Ground_Truth", index=False)

# Plot (GT only)
plt.figure(figsize=(6, 4))
counts = df_gt["MATCHED"].value_counts().sort_index()

bars = plt.bar(
    ["Unmatched", "Matched"],
    counts.values
)

total = counts.sum()
for bar, val in zip(bars, counts.values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{(val / total) * 100:.1f}%",
        ha="center",
        va="bottom",
        fontsize=10
    )

plt.title("CTPTY Counterparty Match Accuracy (Ground Truth Only)")
plt.ylabel("Number of Transactions")
plt.grid(axis="y", alpha=0.3)
plt.savefig(f"{OUT_DIR}/match_accuracy.png", dpi=200, bbox_inches="tight")
plt.close()

# Summary
print("Benchmark complete.")
print(f"Total rows                : {len(df)}")
print(f"GT available rows         : {len(df_gt)}")
print(f"GT unavailable rows       : {len(df_no_gt)}")
print(f"Matched (>= {THRESHOLD})  : {len(df_matched)}")
print(f"Unmatched                 : {len(df_unmatched)}")
print(f"Graph saved to            : {OUT_DIR}/match_accuracy.png")
print(f"Excel saved to            : {EXCEL_OUT}")

