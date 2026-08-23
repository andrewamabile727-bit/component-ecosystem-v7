import streamlit as st
import pandas as pd
import random
import re

st.set_page_config(page_title="Component Ecosystem Code Generator v7.1", layout="wide")

st.title("🧩 Component Ecosystem Code Generator v7.1")
st.markdown("Standardized part number generator and batch code processor.")

# --- 1. CATEGORY NAVIGATION ---
category = st.sidebar.selectbox(
    "Select Category Generator",
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

# Prefix mapping (Mounting & Accessory Parts = 'B')
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

prefix = prefix_map[category]

st.header(f"Generator: {category}")
st.info(f"Outputs 6-character part numbers starting with **{prefix}** (e.g., `{prefix}12345`).")

# --- 2. SINGLE CODE GENERATOR ---
st.subheader("Generate Single Part Number")

col1, col2 = st.columns(2)
with col1:
    part_desc = st.text_input("Part Description / Name", placeholder="e.g., Refrigerator Riser Pad")
with col2:
    digits_input = st.text_input("5-Digit Seed (Leave blank for random)", max_chars=5)

if st.button("Generate Single Part Number"):
    if digits_input:
        cleaned = "".join(filter(str.isdigit, str(digits_input)))
        if len(cleaned) == 5:
            generated_code = f"{prefix}{cleaned}"
        else:
            st.error("Please enter exactly 5 numerical digits.")
            st.stop()
    else:
        rand_num = random.randint(10000, 99999)
        generated_code = f"{prefix}{rand_num}"

    st.success(f"**Generated Part Number:** `{generated_code}`")
    st.code(f"Part No.: {generated_code}\nDescription: {part_desc if part_desc else 'N/A'}", language="text")

st.markdown("---")

# --- 3. BATCH PROCESSING FOR UPLOADED FILE ---
st.header("Master File Cross-Reference & Batch Generator")
uploaded_file = st.file_uploader(f"Upload Item Master / Code CSV for {category}", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        df.columns = [str(c).strip() for c in df.columns]
        
        st.success(f"Loaded CSV successfully ({len(df)} records found).")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Batch Processing Button
        if st.button("🚀 Generate Part Numbers for Uploaded List"):
            code_col = df.columns[0]
            used_seeds = set()

            def process_batch_entry(val, idx):
                s = str(val).strip()
                digits_only = re.sub(r'\D', '', s)
                
                if len(digits_only) >= 5:
                    seed = digits_only[:5]
                else:
                    seed = f"{(idx + 10000) % 90000 + 10000}"
                
                used_seeds.add(seed)
                return f"{prefix}{seed}"

            processed_df = df.copy()
            processed_df["Generated_Part_No"] = [
                process_batch_entry(row[code_col], i) for i, row in df.iterrows()
            ]

            # Reorder columns so Generated_Part_No is first
            cols = ["Generated_Part_No"] + [c for c in processed_df.columns if c != "Generated_Part_No"]
            processed_df = processed_df[cols]

            st.markdown("### Processed Batch Results")
            st.dataframe(processed_df, use_container_width=True, hide_index=True)

            # CSV Download
            csv_bytes = processed_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=f"📥 Download Processed {category} CSV",
                data=csv_bytes,
                file_name=f"{category.replace(' ', '_')}_Generated_Codes.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error loading file: {e}")