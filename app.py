import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Component Ecosystem Code Generator v7.0", layout="wide")

st.title("🧩 Component Ecosystem Code Generator v7.0")
st.markdown("Standardized part number generator and batch code verification.")

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

# Prefix mapping (UPDATED: Mounting & Accessory Parts = 'B')
prefix_map = {
    "Mounting & Accessory Parts": "B",  # Changed from F to B
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
st.subheader("Generate Part Number")

col1, col2 = st.columns(2)
with col1:
    part_desc = st.text_input("Part Description / Name", placeholder="e.g., Refrigerator Riser Pad")
with col2:
    digits_input = st.text_input("5-Digit Seed (Leave blank for random)", max_chars=5)

if st.button("Generate Part Number"):
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

# --- 3. MAIN SCREEN FILE UPLOADER & MASTER SEARCH ---
st.header("Master File Cross-Reference")
uploaded_file = st.file_uploader(f"Upload Item Master / Code CSV for {category}", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        df.columns = [str(c).strip() for c in df.columns]
        
        st.success(f"Loaded CSV successfully ({len(df)} records).")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Quick Search
        search_query = st.text_input("Search Uploaded File", placeholder="Enter Part No or Description...")
        if search_query:
            part_col = df.columns[0]
            matches = df[df[part_col].astype(str).str.contains(search_query, case=False, na=False)]
            st.dataframe(matches, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error loading file: {e}")