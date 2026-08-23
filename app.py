import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Component Ecosystem Code Generator v7.2", layout="wide")

st.title("🧩 Component Ecosystem Code Generator v7.2")
st.markdown("Generate standardized, unique part numbers for manufactured and purchased components.")

# --- 1. FILE UPLOAD & MASTER CHECK ---
st.sidebar.header("Data Integration")
uploaded_file = st.sidebar.file_uploader("Upload Item Master CSV (Optional)", type=["csv"])

master_df = None
existing_part_numbers = set()

if uploaded_file is not None:
    try:
        master_df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        master_df.columns = [str(c).strip() for c in master_df.columns]
        
        # Look for Part No column
        part_col = next((c for c in master_df.columns if "Part No" in c or "Item No" in c), master_df.columns[0])
        existing_part_numbers = set(master_df[part_col].dropna().astype(str).str.strip().unique())
        
        st.sidebar.success(f"Loaded Master File: {len(existing_part_numbers)} unique part numbers indexed.")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")

# --- 2. CATEGORY NAVIGATION ---
st.sidebar.header("Navigation")
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

st.header(f"Generator: {category}")

# Helper function to generate unique digits
def get_unique_part_number(prefix, digits_input=None):
    if digits_input:
        cleaned = "".join(filter(str.isdigit, str(digits_input)))
        if len(cleaned) == 5:
            code = f"{prefix}{cleaned}"
            if code in existing_part_numbers:
                st.warning(f"⚠️ Warning: `{code}` already exists in your uploaded Item Master file!")
            return code
        else:
            st.error("Please enter exactly 5 numerical digits.")
            return None
    
    # Generate random unique 5-digit number
    for _ in range(1000):
        rand_num = random.randint(10000, 99999)
        code = f"{prefix}{rand_num}"
        if code not in existing_part_numbers:
            return code
    
    return f"{prefix}{random.randint(10000, 99999)}"

# ---------------------------------------------------------
# 1. MOUNTING & ACCESSORY PARTS (PREFIX 'B')
# ---------------------------------------------------------
if category == "Mounting & Accessory Parts":
    st.subheader("Mounting & Accessory Parts Part Number Generator")
    st.info("Generates 5-digit part numbers starting with **B** (e.g., B82404, B12345).")

    part_desc = st.text_input("Part Description / Name", placeholder="e.g., Refrigerator Riser Pad")
    digits = st.text_input("5-Digit Seed (Leave blank for random)", max_chars=5)

    if st.button("Generate Part Number"):
        part_no = get_unique_part_number("B", digits if digits else None)
        if part_no:
            st.success(f"**Generated Part Number:** `{part_no}`")
            st.code(f"Part No.: {part_no}\nDescription: {part_desc if part_desc else 'N/A'}", language="text")

# ---------------------------------------------------------
# 2. FRAME TUBES (PREFIX 'F')
# ---------------------------------------------------------
elif category == "Frame Tubes":
    st.subheader("Frame Tubes Part Number Generator")
    st.info("Generates 5-digit part numbers starting with **F** (e.g., F12345).")

    part_desc = st.text_input("Frame Tube Description", placeholder="e.g., Lower Horizontal Frame Support")
    digits = st.text_input("5-Digit Seed (Leave blank for random)", max_chars=5)

    if st.button("Generate Part Number"):
        part_no = get_unique_part_number("F", digits if digits else None)
        if part_no:
            st.success(f"**Generated Part Number:** `{part_no}`")
            st.code(f"Part No.: {part_no}\nDescription: {part_desc if part_desc else 'N/A'}", language="text")

# ---------------------------------------------------------
# 3. OTHER CATEGORIES
# ---------------------------------------------------------
else:
    prefix_map = {
        "Sheet Metal & Sheaths": "S",
        "Interior Lining & Wall Coverings": "I",
        "Trim & Corner Guards": "T",
        "J-Channels & Edge Extrusions": "J",
        "Fasteners & Hardware": "K",
        "Concrete Composite Mixes": "K"
    }
    
    p_prefix = prefix_map.get(category, "X")
    st.subheader(f"{category} Part Number Generator")
    st.info(f"Generates 5-digit part numbers starting with **{p_prefix}** (e.g., {p_prefix}12345).")

    part_desc = st.text_input("Item Description", placeholder="Enter item description...")
    digits = st.text_input("5-Digit Seed (Leave blank for random)", max_chars=5)

    if st.button("Generate Part Number"):
        part_no = get_unique_part_number(p_prefix, digits if digits else None)
        if part_no:
            st.success(f"**Generated Part Number:** `{part_no}`")
            st.code(f"Part No.: {part_no}\nDescription: {part_desc if part_desc else 'N/A'}", language="text")

# --- 3. MASTER FILE SEARCH (IF FILE UPLOADED) ---
if master_df is not None:
    st.markdown("---")
    st.subheader("🔍 Search Uploaded Item Master")
    search_query = st.text_input("Search Item Master by Part No or Description", placeholder="e.g., B82404 or Riser Pad")
    if search_query:
        part_col = next((c for c in master_df.columns if "Part No" in c or "Item No" in c), master_df.columns[0])
        desc_col = next((c for c in master_df.columns if "Desc" in c), master_df.columns[1] if len(master_df.columns) > 1 else master_df.columns[0])
        
        matches = master_df[
            master_df[part_col].astype(str).str.contains(search_query, case=False, na=False) |
            master_df[desc_col].astype(str).str.contains(search_query, case=False, na=False)
        ]
        st.dataframe(matches, use_container_width=True, hide_index=True)