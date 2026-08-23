import streamlit as st
import pandas as pd
import random
import io

st.set_page_config(page_title="Component Ecosystem Code Generator v7.3", layout="wide")

st.title("🧩 Component Ecosystem Code Generator v7.3")
st.markdown("Standardized part number generator and batch code converter.")

# --- 1. MAIN SCREEN FILE UPLOAD & BATCH CONVERTER ---
st.header("1. Batch Master File Processing")
uploaded_file = st.file_uploader("Upload Item Master / Component CSV File", type=["csv"])

master_df = None
existing_part_numbers = set()

if uploaded_file is not None:
    try:
        master_df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        master_df.columns = [str(c).strip() for c in master_df.columns]
        
        # Identify Part No and Category/Description columns
        part_col = next((c for c in master_df.columns if "Part No" in c or "Item No" in c), master_df.columns[0])
        desc_col = next((c for c in master_df.columns if "Desc" in c), master_df.columns[1] if len(master_df.columns) > 1 else master_df.columns[0])
        
        st.success(f"Loaded CSV file successfully ({len(master_df)} total records found).")

        # Automatically update any Mounting & Accessory F-codes to B-codes in batch
        updated_df = master_df.copy()
        
        def convert_mounting_prefix(part_str, desc_str):
            part_str = str(part_str).strip()
            desc_str = str(desc_str).strip().lower()
            
            # Check if part starts with F and is a mounting/accessory item
            # OR convert F to B for 5-digit numerical seeds if specified
            if part_str.startswith('F') and len(part_str) == 6 and part_str[1:].isdigit():
                # Swap F to B
                return f"B{part_str[1:]}"
            return part_str

        # Option to perform automatic batch prefix conversion
        st.subheader("Batch Prefix Conversion (F → B for Mounting Parts)")
        if st.checkbox("Automatically convert 'F' prefix to 'B' prefix for 5-digit parts", value=True):
            updated_df[part_col] = [
                convert_mounting_prefix(p, d) 
                for p, d in zip(updated_df[part_col], updated_df[desc_col])
            ]
            st.info("Updated Part Numbers starting with 'F' to 'B' across the loaded table.")

        # Display full updated dataframe
        st.dataframe(updated_df, use_container_width=True, hide_index=True)

        # Download button for updated CSV
        csv_bytes = updated_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Download Updated Master CSV",
            data=csv_bytes,
            file_name="Item_Master_Updated_B_Prefix.csv",
            mime="text/csv"
        )

        existing_part_numbers = set(updated_df[part_col].dropna().astype(str).str.strip().unique())

    except Exception as e:
        st.error(f"Error processing file: {e}")

st.markdown("---")

# --- 2. SINGLE PART NUMBER GENERATOR ---
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

st.info(f"Category: **{category}** | Selected Prefix: **{prefix}** (Outputs e.g., `{prefix}12345`)")

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
        # Generate random unique 5-digit number
        rand_num = random.randint(10000, 99999)
        generated_code = f"{prefix}{rand_num}"

    # Duplicate check against uploaded file
    if generated_code in existing_part_numbers:
        st.warning(f"⚠️ `{generated_code}` already exists in your uploaded file!")
    else:
        st.success(f"**Generated Part Number:** `{generated_code}`")

    st.code(f"Part No.: {generated_code}\nDescription: {part_desc if part_desc else 'N/A'}", language="text")