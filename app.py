import streamlit as st
import pandas as pd
import random
import re

st.set_page_config(page_title="Component Ecosystem Code Generator", layout="wide")

st.title("🧩 Component Ecosystem Code Generator")
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

# --- 2. PREFIX MAPPING ---
prefix_map = {
    "Mounting & Accessory Parts": "B",  # B-Prefix for Mounting & Accessory Parts
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

# --- 3. SINGLE CODE GENERATOR ---
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

# --- 4. BATCH GENERATOR & DOWNLOAD ---
st.header("Master File Batch Generator")

col_up1, col_up2 = st.columns([2, 1])
with col_up1:
    uploaded_file = st.file_uploader(f"Upload Item Master / Code CSV for {category}", type=["csv"])
with col_up2:
    start_seed_input = st.text_input("Starting 5-Digit Seed (Default: 10001)", value="10001", max_chars=5)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        df.columns = [str(c).strip() for c in df.columns]
        
        st.success(f"Loaded CSV successfully ({len(df)} records found).")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Action Button to Process Batch
        if st.button("🚀 Generate Unique Part Numbers for Uploaded List"):
            # Parse starting seed
            cleaned_start = "".join(filter(str.isdigit, str(start_seed_input)))
            current_seed = int(cleaned_start) if len(cleaned_start) == 5 else 10001
            
            generated_codes = []
            used_codes = set()

            # Assign sequential unique codes to every row to guarantee zero duplicates
            for _ in range(len(df)):
                while True:
                    candidate = f"{prefix}{current_seed:05d}"
                    current_seed += 1
                    if candidate not in used_codes:
                        used_codes.add(candidate)
                        generated_codes.append(candidate)
                        break

            processed_df = df.copy()
            processed_df["Generated_Part_No"] = generated_codes

            # Move Generated_Part_No to the first column for easy reading
            cols = ["Generated_Part_No"] + [c for c in processed_df.columns if c != "Generated_Part_No"]
            processed_df = processed_df[cols]

            st.markdown("### Processed Batch Results (Guaranteed Unique)")
            st.dataframe(processed_df, use_container_width=True, hide_index=True)

            # Generate Clean File Name (Removing "&" and spaces)
            safe_category_name = category.replace(" & ", "_").replace(" ", "_")
            file_name = f"{safe_category_name}_Generated_Codes.csv"

            # Generate Download Button using standard utf-8 to prevent Excel errors
            csv_bytes = processed_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Download Processed {category} CSV",
                data=csv_bytes,
                file_name=file_name,
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error loading file: {e}")