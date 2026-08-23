import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Component Ecosystem Code Generator v7.4", layout="wide")

st.title("🧩 Component Ecosystem Code Generator v7.4")
st.markdown("Standardized part number generator and prefix converter (`F` → `B`).")

# --- 1. BATCH FILE PROCESSING & CONVERTER ---
st.header("1. Batch Master File Converter")
uploaded_file = st.file_uploader("Upload Master File / Code CSV", type=["csv"])

existing_codes = set()

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        df.columns = [str(c).strip() for c in df.columns]
        
        # Auto-detect code column (MasterCode, Part No, or first column)
        code_col = next((c for c in df.columns if any(k in c.lower() for k in ["mastercode", "part", "code", "item"])), df.columns[0])
        
        st.success(f"File loaded successfully. Detected target column: `{code_col}` ({len(df)} records).")

        # Conversion logic for both structured (F-00.00...) and simple (F12345) codes
        def convert_code(val):
            s = str(val).strip()
            if s.startswith("F-"):
                return "B-" + s[2:]
            elif s.startswith("F"):
                return "B" + s[1:]
            return s

        # Generate converted column
        converted_df = df.copy()
        converted_df["Original_Code"] = df[code_col]
        converted_df[code_col] = df[code_col].apply(convert_code)

        # Show comparison view
        st.subheader("Conversion Preview (F → B Prefix Swap)")
        
        diff_count = (converted_df["Original_Code"] != converted_df[code_col]).sum()
        st.info(f"Updated **{diff_count}** part numbers to the **`B`** prefix while preserving all remaining digits and characters.")

        # Display preview table
        preview_cols = ["Original_Code", code_col] + [c for c in df.columns if c != code_col]
        st.dataframe(converted_df[preview_cols], use_container_width=True, hide_index=True)

        # Download clean CSV with updated codes
        export_df = converted_df.drop(columns=["Original_Code"])
        csv_bytes = export_df.to_csv(index=False).encode('utf-8-sig')
        
        st.download_button(
            label="📥 Download Converted CSV (B-Prefix)",
            data=csv_bytes,
            file_name="Item_Master_Updated_B_Prefix.csv",
            mime="text/csv"
        )

        existing_codes = set(export_df[code_col].dropna().astype(str).str.strip().unique())

    except Exception as e:
        st.error(f"Error reading CSV file: {e}")

st.markdown("---")

# --- 2. SINGLE CODE GENERATOR & CONVERTER ---
st.header("2. Single Code Generator / Converter")

category = st.selectbox(
    "Select Component Category",
    [
        "Mounting & Accessory Parts",
        "Frame Tubes",
        "Sheet Metal & Sheaths",
        "Interior Lining & Wall Coverings",
        "Trim & Corner Guards",
        "J-Channels & Edge Extrusions",
        "Fasteners & Hardware",
        "Concrete Composite Mixes"
    ]
)

prefix_map = {
    "Mounting & Accessory Parts": "B",
    "Frame Tubes": "F",
    "Sheet Metal & Sheaths": "S",
    "Interior Lining & Wall Coverings": "I",
    "Trim & Corner Guards": "T",
    "J-Channels & Edge Extrusions": "J",
    "Fasteners & Hardware": "K",
    "Concrete Composite Mixes": "K"
}

target_prefix = prefix_map[category]

st.info(f"Selected Category: **{category}** | Active Prefix: **`{target_prefix}`**")

col1, col2 = st.columns(2)
with col1:
    part_desc = st.text_input("Part Description / Name", placeholder="e.g., Refrigerator Riser Pad")
with col2:
    code_input = st.text_input("Enter Existing Code or Seed (e.g., F-00.00A1... or 82404)", placeholder="Leave blank for random 5-digit seed")

if st.button("Generate / Convert Part Number"):
    raw_val = code_input.strip() if code_input else ""
    
    if raw_val:
        # If user pasted an existing code starting with F- or F, convert it to target prefix
        if raw_val.startswith("F-"):
            new_code = f"{target_prefix}-" + raw_val[2:]
        elif raw_val.startswith("F"):
            new_code = f"{target_prefix}" + raw_val[1:]
        elif raw_val.startswith(f"{target_prefix}-") or raw_val.startswith(target_prefix):
            new_code = raw_val
        else:
            # Otherwise attach the target prefix directly
            new_code = f"{target_prefix}-{raw_val}" if "-" in raw_val else f"{target_prefix}{raw_val}"
    else:
        # Generate random 5-digit number with target prefix
        rand_num = random.randint(10000, 99999)
        new_code = f"{target_prefix}{rand_num}"

    if new_code in existing_codes:
        st.warning(f"⚠️ `{new_code}` already exists in the uploaded file!")
    else:
        st.success(f"**Generated / Converted Part Number:** `{new_code}`")

    st.code(f"Part No.: {new_code}\nDescription: {part_desc if part_desc else 'N/A'}", language="text")