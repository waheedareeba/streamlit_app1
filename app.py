import streamlit as st
import pandas as pd
import io
from search_parts import load_excel, search_in_df
from xlsxwriter.utility import xl_col_to_name


# Create columns for logo and title
col1, col2 = st.columns([1.5, 6])  # Adjust width ratio
with col1:
    st.image("logo.jpg", width=150)

with col2:
    st.markdown(
        """
        <h1 style='margin-bottom: 0px; padding-top: 70px;'> 🔍 Part Number Search Tool</h1>
        """,
        unsafe_allow_html=True
    )

# Add some space before the steps
st.markdown("<br>", unsafe_allow_html=True)

# Steps section
st.markdown("""
**Step 1**: Upload the file containing part numbers (CSV or Excel)  
**Step 2**: Upload one catalog file to search in  
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
            col_to_use = None
            for col in ['Part Number', 'P/N', 'Item Number', 'PART#','Reference','Codigo']:
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
                    all_res = res1  # Extend if using more files later

                    if all_res:
                        for match in all_res:
                            # Flatten row for download
                            row_data = match["matched_row"].copy()
                            row_data = {k: v for k, v in row_data.items() if not str(k).startswith("Unnamed")}
                            row_data["Original Part"] = match["original_part"]
                            row_data["Variant Used"] = match["variant_used"]
                           
                            download_rows.append(row_data)
                    else:
                        # Add placeholder row for unmatched part
                        download_rows.append({
                            "Original Part": part,
                            "Variant Used": "No match",
        
                
                        })

                if download_rows:
                    output_df = pd.DataFrame(download_rows)
                    

                    # Ensure "Original Part" is the first column
                    columns = output_df.columns.tolist()
                    if "Original Part" in columns:
                        columns.remove("Original Part")
                        columns = ["Original Part"] + columns
                        output_df = output_df[columns]

                    buffer = io.BytesIO()
                
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        output_df.to_excel(writer, index=False, sheet_name='Part_Number_Match')
                    buffer.seek(0)
                    

                    st.download_button(
                        label="📥 Download Results as Excel",
                        data=buffer,
                        file_name="Part_Number_Match.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("⚠️ No matches found.")
    else:
        st.warning("⚠️ Please upload both the part number file and catalog file.")
