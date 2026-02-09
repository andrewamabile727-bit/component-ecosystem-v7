import streamlit as st
import pandas as pd
import io

# --- 1. ENGINE V7.0 (THE BRAIN) ---
def poly_hash_v7(string_in, modulo=100000):
    """Generates a 5-digit unique numerical code (00000-99999)"""
    h = 0
    # Removes dashes, spaces, and makes everything uppercase for a perfect match
    clean_str = str(string_in).upper().replace("-", "").replace(" ", "")
    for char in clean_str:
        h = (h * 53 + ord(char))
    h += len(clean_str)
    return f"{h % modulo:03d}" if modulo == 1000 else f"{h % modulo:05d}"

# --- 2. APP CONFIGURATION ---
st.set_page_config(page_title="Component Ecosystem v7.0", layout="wide")
st.title("🧩 Component Ecosystem v7.0")
st.markdown("### Sub-Tier & Component Level Master Control")

# Sidebar for Category selection
category_data = {
    "Frame Tubes": "F",
    "Connector Comp.": "M",
    "Connector Assy": "N",
    "Ext. Cabinet Sheathing": "S",
    "Int. Cabinet Sheathing": "I",
    "Trim": "T",
    "J-Channel": "J",
    "Mounting & Accessory Parts": "B",
    "Packaging": "R",
    "Accessories/UX Kit": "U"
}

category = st.sidebar.selectbox("Select Component Category", list(category_data.keys()))
prefix = category_data[category]

# --- 3. DATA PROCESSING ---
uploaded_file = st.file_uploader(f"Upload {category} CSV", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # 5th Grade Safety Check: Make sure the MasterCode column exists
    if "MasterCode" not in df.columns:
        st.error("❌ Error: Your CSV file is missing the 'MasterCode' column!")
        st.info("Please rename your column to 'MasterCode' and try again.")
    else:
        if st.button("🚀 Generate Component IDs"):
            # Create the ID: Hard Prefix + 5-digit number
            df['Component ID'] = df['MasterCode'].apply(lambda x: f"{prefix}{poly_hash_v7(x)}")
            
            # Check for duplications (Twin Check)
            duplicates = df.duplicated(subset=['Component ID']).sum()
            
            st.success(f"✅ IDs Generated for {category}!")
            
            if duplicates > 0:
                st.warning(f"⚠️ Warning: Found {duplicates} duplicate IDs in this list.")
            else:
                st.info("✨ Clean Batch: Zero duplicates detected.")
            
            st.dataframe(df)
            
            # Download Button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Component List",
                data=csv,
                file_name=f"{category.replace(' ', '_')}_Export.csv",
                mime='text/csv'
            )
