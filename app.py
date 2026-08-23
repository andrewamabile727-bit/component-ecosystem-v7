import streamlit as st
import random

st.set_page_config(page_title="Component Ecosystem Code Generator v7.1", layout="wide")

st.title("🧩 Component Ecosystem Code Generator v7.1")
st.markdown("Generate standardized, unique part numbers for manufactured and purchased components.")

# Sidebar Navigation
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

# ---------------------------------------------------------
# 1. MOUNTING & ACCESSORY PARTS (UPDATED TO PREFIX 'B')
# ---------------------------------------------------------
if category == "Mounting & Accessory Parts":
    st.subheader("Mounting & Accessory Parts Part Number Generator")
    st.info("Generates 5-digit part numbers starting with **B** (e.g., B12345).")

    part_desc = st.text_input("Part Description / Name", placeholder="e.g., Refrigerator Riser Pad")
    
    # Custom or random 5-digit seed
    digits = st.text_input("5-Digit Seed (Leave blank for random)", max_chars=5)

    if st.button("Generate Part Number"):
        if not digits:
            rand_num = random.randint(10000, 99999)
        else:
            # Clean non-digit characters if entered
            cleaned_digits = "".join(filter(str.isdigit, digits))
            if len(cleaned_digits) == 5:
                rand_num = cleaned_digits
            else:
                st.error("Please enter exactly 5 numerical digits.")
                st.stop()

        # Prefix forced to 'B' to avoid collision with Frame Tubes ('F')
        part_no = f"B{rand_num}"
        
        st.success(f"**Generated Part Number:** `{part_no}`")
        st.code(f"Part No.: {part_no}\nDescription: {part_desc if part_desc else 'N/A'}", language="text")

# ---------------------------------------------------------
# 2. FRAME TUBES (KEEP PREFIX 'F')
# ---------------------------------------------------------
elif category == "Frame Tubes":
    st.subheader("Frame Tubes Part Number Generator")
    st.info("Generates 5-digit part numbers starting with **F** (e.g., F12345).")

    part_desc = st.text_input("Frame Tube Description", placeholder="e.g., Lower Horizontal Frame Support")
    digits = st.text_input("5-Digit Seed (Leave blank for random)", max_chars=5)

    if st.button("Generate Part Number"):
        if not digits:
            rand_num = random.randint(10000, 99999)
        else:
            cleaned_digits = "".join(filter(str.isdigit, digits))
            if len(cleaned_digits) == 5:
                rand_num = cleaned_digits
            else:
                st.error("Please enter exactly 5 numerical digits.")
                st.stop()

        part_no = f"F{rand_num}"
        st.success(f"**Generated Part Number:** `{part_no}`")
        st.code(f"Part No.: {part_no}\nDescription: {part_desc if part_desc else 'N/A'}", language="text")

# ---------------------------------------------------------
# 3. OTHER CATEGORIES (STANDARDIZED PREFIXES)
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
        if not digits:
            rand_num = random.randint(10000, 99999)
        else:
            cleaned_digits = "".join(filter(str.isdigit, digits))
            if len(cleaned_digits) == 5:
                rand_num = cleaned_digits
            else:
                st.error("Please enter exactly 5 numerical digits.")
                st.stop()

        part_no = f"{p_prefix}{rand_num}"
        st.success(f"**Generated Part Number:** `{part_no}`")
        st.code(f"Part No.: {part_no}\nDescription: {part_desc if part_desc else 'N/A'}", language="text")