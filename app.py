import streamlit as st
import pandas as pd
import random
import re

st.set_page_config(page_title="Component Ecosystem Code Generator", layout="wide")

st.title("🧩 Component Ecosystem Code Generator")
st.markdown("Standardized part number generator and batch code processor.")

# --- 1. SESSION STATE INITIALIZATION ---
if "processed_df" not in st.session_state:
    st.session_state.processed_df = None
if "current_category" not in st.session_state:
    st.session_state.current_category = ""

# --- 2. CATEGORY NAVIGATION ---
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

# Reset session state if category changes
if st.session_state.current_category != category:
    st.session_state.processed_df = None
    st.session_state.current_category = category

# --- 3. PREFIX MAPPING ---
prefix_map = {
    "Mounting & Accessory Parts": "B",  # B-Prefix
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
st.info(f"Outputs 6-character part numbers starting with **{prefix}** (e.g., `{prefix}82404`).")

# --- 4. MASTER CODE HASHING ENGINE ---
def hash_to_5_digits(string):
    """Deterministic hashing logic to convert MasterCode into a unique 5-digit seed."""
    h = 0
    clean_str = str(string).upper().replace("-", "")
    for char in clean_str:
        h = (h * 53 + ord(char))
    h += len(clean_str)
    return f"{h % 100000:05d}"

# --- 5. SINGLE CODE GENERATOR ---
st.subheader("Generate Single Part Number")

col1, col2 = st.columns(2)
with col1:
    part_desc = st.text_input("Part Description / Name", placeholder="e.g., Refrigerator Riser Pad")
with col2:
    master_or_seed = st.text_input("Enter MasterCode or 5-Digit Seed (Leave blank for random)")

if st.button("Generate Single Part Number"):
    raw_val = master_or_seed.strip()
    
    if raw_val:
        if len(raw_val) == 5 and raw_val.isdigit():
            generated_code = f"{prefix}{raw_val}"
        else:
            seed = hash_to_5_digits(raw_val)
            generated_code = f"{prefix}{seed}"
    else:
        rand_num = random.randint(10000, 99999)
        generated_code = f"{prefix}{rand_num}"

    st.success(f"**Generated Part Number:** `{generated_code}`")
    st.code(f"Part No.: {generated_code}\nDescription: {part_desc if part_desc else 'N/A'}", language="text")

st.markdown("---")

# --- 6. BATCH GENERATOR & PERSISTENT VIEW ---
st.header("Master File Batch Generator")

uploaded_file = st.file_uploader(f"Upload Item Master / Code CSV for {category}", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        df.columns = [str(c).strip() for c in df.columns]
        
        st.success(f"Loaded CSV successfully ({len(df)} records found).")

        # Process Batch when button is clicked and store in session_state
        if st.button("🚀 Process MasterCodes for Uploaded List"):
            code_col = df.columns[0]
            
            generated_codes = []
            for val in df[code_col]:
                seed = hash_to_5_digits(val)
                generated_codes.append(f"{prefix}{seed}")

            processed_df = df.copy()
            processed_df["Generated_Part_No"] = generated_codes

            cols = ["Generated_Part_No"] + [c for c in processed_df.columns if c != "Generated_Part_No"]
            st.session_state.processed_df = processed_df[cols]

        # Display results from session_state so they never disappear on download
        if st.session_state.processed_df is not None:
            st.markdown("### Processed Batch Results (Hash Logic)")
            st.dataframe(st.session_state.processed_df, use_container_width=True, hide_index=True)

            # Generate Safe Clean File Name
            safe_category_name = category.replace(" & ", "_").replace(" ", "_")
            file_name = f"{safe_category_name}_Generated_Codes.csv"

            # Export using clean UTF-8-sig encoding so Excel reads it properly without file errors
            csv_bytes = st.session_state.processed_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=f"📥 Download Processed {category} CSV",
                data=csv_bytes,
                file_name=file_name,
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error loading file: {e}")