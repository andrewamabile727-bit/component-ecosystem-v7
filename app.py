import streamlit as st
import pandas as pd
import random
import re

st.set_page_config(page_title="Component Ecosystem Code Generator v7.5", layout="wide")

st.title("🧩 Component Ecosystem Code Generator")
st.markdown("Batch master code converter and 6-character part number generator.")

# --- 1. BATCH FILE CONVERTER (MAIN SCREEN) ---
st.header("1. Batch Master File Converter")
uploaded_file = st.file_uploader("Upload Item Master / Code CSV File", type=["csv"])

existing_codes = set()

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        df.columns = [str(c).strip() for c in df.columns]
        
        # Detect part number column
        code_col = next((c for c in df.columns if any(k in c.lower() for k in ["mastercode", "part", "code", "item"])), df.columns[0])
        
        # Function to generate 6-character B-code (B + 5 digits)
        used_seeds = set()
        
        def format_to_6char_b(val):
            s = str(val).strip()
            # Extract digits from the input string
            digits_only = re.sub(r'\D', '', s)
            
            if len(digits_only) >= 5:
                # Take 5 digits
                seed = digits_only[:5] if len(digits_only) == 5 else digits_only[-5:]
            else:
                # Generate unique 5 digits if fewer than 5 exist
                while True:
                    seed = str(random.randint(10000, 99999))
                    if seed not in used_seeds:
                        break
            
            used_seeds.add(seed)
            return f"B{seed}"

        # Apply conversion
        converted_df = df.copy()
        converted_df[code_col] = [format_to_6char_b(val) for val in df[code_col]]

        # Display converted table
        st.dataframe(converted_df, use_container_width=True, hide_index=True)

        # Download button for converted file
        csv_bytes = converted_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Download Converted Master CSV (B-Prefix)",
            data=csv_bytes,
            file_name="Item_Master_B_Prefix_6Char.csv",
            mime="text/csv"
        )

        existing_codes = set(converted_df[code_col].dropna().astype(str).str.strip().unique())

    except Exception as e:
        st.error(f"Error processing CSV file: {e}")

st.markdown("---")

# --- 2. SINGLE CODE GENERATOR ---
st.header("2. Single Part Number Generator")

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

prefix = prefix_map[category]

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

    if generated_code in existing_codes:
        st.warning(f"⚠️ `{generated_code}` already exists in the uploaded file!")
    else:
        st.success(f"**Generated Part Number:** `{generated_code}`")

    st.code(f"Part No.: {generated_code}\nDescription: {part_desc if part_desc else 'N/A'}", language="text")