import pandas as pd
import re

def load_excel(file_obj):
    #return pd.read_excel(file_obj,header=9,)
    return pd.read_excel(file_obj)



def generate_variants(part):
    variants = set()
    variants.add(part.strip())

    if len(part) > 3:
        variants.add(part[:3] + '-' + part[3:])

    variants.add(re.sub(r'[A-Za-z]', '', part))

    return list(variants)


'''
def generate_variants(part):
    variants = set()

    part = part.strip()
    variants.add(part)

    trimmed_part = re.sub(r'^0+|0+$', '', part)
    if trimmed_part != part:
        variants.add(trimmed_part)

        # Apply transformations on trimmed part
        if len(trimmed_part) > 3:
            variants.add(trimmed_part[:3] + '-' + trimmed_part[3:])
        variants.add(re.sub(r'[A-Za-z]', '', trimmed_part))

    # Apply original transformations on full part
    if len(part) > 3:
        variants.add(part[:3] + '-' + part[3:])

    variants.add(re.sub(r'[A-Za-z]', '', part))

    return list(variants)
'''

def search_in_df(part, df, source_name, possible_columns=None):
   
    if possible_columns is None:
        possible_columns = ['Part Number', 'Item Number', 'Part #','Part No']

    found_column = None
    print(df.columns)
    for col in df.columns:
        if col.strip() in possible_columns:
            found_column = col
            break

    if not found_column:
        raise ValueError(f"No valid part number column found in {source_name}. Expected one of: {possible_columns}")

    variants = generate_variants(part)
    results = []

    for variant in variants:
        matches = df[df[found_column].astype(str).str.contains(variant, case=False, na=False)]
        if not matches.empty:
            for _, row in matches.iterrows():
                results.append({
                    "original_part": part,
                    "variant_used": variant,
                    "source_file": source_name,
                    "matched_row": row.to_dict()
                })
    return results