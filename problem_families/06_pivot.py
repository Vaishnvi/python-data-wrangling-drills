"""
Problem Family 6 - Pivot Long Rows into a Wide Table
====================================================
Input is "long" format: one row per (index, pivot, value).
Output is "wide" format: one row per index value, one column per pivot value.

    Date,Product,Sales            Date,A,B,C
    2024-01-01,A,100              2024-01-01,100,150,200
    2024-01-01,B,150      --->    2024-01-02,120,130,None
    2024-01-01,C,200
    ...

Approach (O(n + rows*cols)):
    1. Collect the sorted set of distinct pivot values -> the output columns.
    2. Group values into a dict keyed by (index, pivot).
    3. Emit one dict per index value, filling missing cells with a default.

Run:
    python 06_pivot.py
"""

from collections import defaultdict

data = [
    {"Date": "2024-01-01", "Product": "A", "Sales": 100},
    {"Date": "2024-01-01", "Product": "B", "Sales": 150},
    {"Date": "2024-01-01", "Product": "C", "Sales": 200},
    {"Date": "2024-01-02", "Product": "A", "Sales": 120},
    {"Date": "2024-01-02", "Product": "B", "Sales": 130},
]


def pivot_table(data, index_col, pivot_col, value_col, fill=None):
    """Pivot a list of dicts from long to wide format.

    Parameters
    ----------
    data       : list of dicts (each dict is one row)
    index_col  : column whose values become the output ROWS
    pivot_col  : column whose values become the output COLUMNS
    value_col  : column whose values fill the cells
    fill       : value for (row, column) pairs that have no data

    If several input rows share the same (index, pivot) pair their values are
    SUMMED, which is the usual spreadsheet behaviour.

    Returns a list of dicts, one per index value in sorted order, e.g.
        {"Date": "2024-01-01", "A": 100, "B": 150, "C": 200}
    """
    # 1. Output columns: every distinct pivot value, in a stable order.
    columns = sorted({row[pivot_col] for row in data})

    # 2. Aggregate values by (index, pivot). defaultdict(int) starts at 0 so we
    #    can += without checking whether the key exists yet.
    cells = defaultdict(int)
    for row in data:
        cells[(row[index_col], row[pivot_col])] += row[value_col]

    # 3. One output row per index value, in sorted order, with every column present.
    index_values = sorted({row[index_col] for row in data})
    wide = []
    for idx in index_values:
        out_row = {index_col: idx}
        for col in columns:
            out_row[col] = cells.get((idx, col), fill)
        wide.append(out_row)
    return wide


res = pivot_table(data, index_col="Date", pivot_col="Product", value_col="Sales")

for row in res:
    print(row)

# Render it as CSV text to match the target shape.
columns = [k for k in res[0] if k != "Date"]
print(",".join(["Date"] + columns))
for row in res:
    print(",".join(str(row[k]) for k in ["Date"] + columns))


"""
Expected output
---------------
{'Date': '2024-01-01', 'A': 100, 'B': 150, 'C': 200}
{'Date': '2024-01-02', 'A': 120, 'B': 130, 'C': None}
Date,A,B,C
2024-01-01,100,150,200
2024-01-02,120,130,None
"""
