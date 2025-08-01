import pandas as pd
import re

def load_excel(file_obj):
    
    return pd.read_excel(file_obj)

def search_in_df(part, df, source_name, possible_columns=None):
    if possible_columns is None:
        possible_columns = ['Part Number', 'Item Number', 'Part #', 'Part No', 'P/N', 'PART#']

    found_column = None
    for col in df.columns:
        if col.strip() in possible_columns:
            found_column = col
            break
    if not found_column:
        raise ValueError(f"No valid part number column found in {source_name}. Expected one of: {possible_columns}")

    results = []
    part_clean = part.strip().upper()
    part_digits = re.sub(r'\D', '', part_clean)  

    col_series = df[found_column].astype(str).str.strip()

    exact_mask = col_series == part_clean
    if exact_mask.any():
        for _, row in df[exact_mask].iterrows():
            results.append({
                "original_part": part,
                "variant_used": part_clean,
                "matched_row": row.to_dict(),
                "source": source_name,
                "match_type": "Exact"
            })

    # Numeric match (avoid duplicates)
    if part_digits:
        for idx, val in col_series.items():
            val_digits = re.sub(r'\D', '', val)
            if val_digits == part_digits and not (col_series[idx] == part_clean):
                results.append({
                    "original_part": part,
                    "variant_used": val_digits,
                    "matched_row": df.loc[idx].to_dict(),
                    "source": source_name,
                    "match_type": "Numeric"
                })

    return results


