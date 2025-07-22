import streamlit as st
import pandas as pd
import io
from search_parts import load_excel, search_in_df

st.title("🔍 Part Number Multi-File Search Tool")

st.markdown("""
**Step 1**: Upload the file containing part numbers (CSV or Excel)  
**Step 2**: Upload one or more catalog files to search in  
**Step 3**: Click Search to view results  
*Make sure all files have a column named `Part Number`, `P/N`, `Item Number`, or `PART#`*
""")

# Upload files
part_file = st.file_uploader("Upload part numbers file (Excel or CSV)", type=["xlsx", "csv"])
file1 = st.file_uploader("Upload First Catalog File (Excel)", type=["xlsx"])

if st.button("🔍 Search"):

    if part_file is not None and file1 is not None:
        try:
            if part_file.name.endswith(".csv"):
                parts_df = pd.read_csv(part_file)
            else:
                parts_df = pd.read_excel(part_file, engine="openpyxl")
        except Exception as e:
            st.error(f"❌ Failed to read the uploaded part file: {e}")
        else:
            # Detect usable column
            col_to_use = None
            for col in ['Part Number', 'P/N', 'Item Number', 'PART#']:
                if col in parts_df.columns:
                    col_to_use = col
                    break

            if col_to_use is None:
                st.error("❌ No valid part number column found. Please include a column like 'Part Number', 'P/N', or 'Item Number'.")
            else:
                part_numbers = parts_df[col_to_use].dropna().astype(str).tolist()
                df1 = load_excel(file1)

                download_rows = []

                for part in part_numbers:
                    res1 = search_in_df(part, df1, "File 1")
                    all_res = res1  # You can extend this if using more files

                    if all_res:
                        for match in all_res:

                            # Flatten row for download
                            row_data = match["matched_row"].copy()
                            row_data["Original Part"] = match["original_part"]
                            row_data["Variant Used"] = match["variant_used"]
                            row_data["Source File"] = match["source_file"]
                            download_rows.append(row_data)
                    else:
                        pass

                if download_rows:
                    output_df = pd.DataFrame(download_rows)
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        output_df.to_excel(writer, index=False, sheet_name='Matches')
                    buffer.seek(0)

                    st.download_button(
                        label="📥 Download Results as Excel",
                        data=buffer,
                        file_name="matched_parts.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("⚠️ No matches found.")
    else:
        st.warning("⚠️ Please upload both the part number file and catalog file.")
