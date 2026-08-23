import streamlit as st
import pandas as pd
import re
import os

st.set_page_config(page_title="BOM Professional & Costing Tool", layout="wide")

st.title("🚀 BOM Professional & Costing Tool")
st.markdown("Select a **Sub-Assembly** or **SKU** to generate the complete multi-level BOM waterfall roll-up.")

# --- 1. DEFAULT CSV FILE NAMES ---
MASTER_FILE = "Item_Master_v4_Template.csv"
LINKS_FILE = "BOM_Links_v4_Template.csv"
SKU_FILE = "L0&L1 Skus..xlsx - Sheet1.csv"

# Optional File Uploaders in Sidebar if user wants to swap files on the fly
st.sidebar.header("Data Source Setup")
uploaded_master = st.sidebar.file_uploader("Upload Item Master (CSV)", type=["csv"])
uploaded_links = st.sidebar.file_uploader("Upload BOM Links (CSV)", type=["csv"])

# --- 2. DATA LOADING ENGINE ---
@st.cache_data(ttl=1)
def load_data():
    # Prioritize uploaded files, fallback to repo hardcoded files
    f_m = uploaded_master if uploaded_master is not None else (MASTER_FILE if os.path.exists(MASTER_FILE) else None)
    f_l = uploaded_links if uploaded_links is not None else (LINKS_FILE if os.path.exists(LINKS_FILE) else None)
    f_s = SKU_FILE if os.path.exists(SKU_FILE) else None

    if f_m is None or f_l is None:
        return None, None, None

    # Load CSVs
    df_m = pd.read_csv(f_m, encoding='utf-8-sig').apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df_l = pd.read_csv(f_l, encoding='utf-8-sig').apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    
    df_s = None
    if f_s:
        try:
            df_s = pd.read_csv(f_s, encoding='utf-8-sig').apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        except Exception:
            df_s = None

    # Clean Header Titles
    for df in [df_m, df_l]:
        df.columns = [str(c).strip() for c in df.columns]
        df.drop(columns=[c for c in df.columns if 'Unnamed' in c or c == ''], inplace=True, errors='ignore')

    if df_s is not None:
        df_s.columns = [str(c).strip() for c in df_s.columns]

    # Clean Unit Cost Column
    cost_col = next((c for c in df_m.columns if "Cost" in c), "Unit Cost")
    df_m['Math_Cost'] = df_m[cost_col].replace(r'[^\d.]', '', regex=True).replace('', '0').astype(float)

    return df_m, df_l, df_s

df_m, df_l, df_s = load_data()

if df_m is None or df_l is None:
    st.error("🚨 Missing required data files. Please upload your `Item Master` and `BOM Links` CSV files or ensure they exist in your GitHub repository.")
    st.stop()

# --- 3. BUILD LOOKUP DICTIONARIES & TREE ---
# drop_duplicates prevents index crashes if part numbers repeat in Item Master
master_map = df_m.drop_duplicates(subset=['Part No.']).set_index('Part No.').to_dict('index')

bom_tree = {}
for _, row in df_l.iterrows():
    parent = str(row.iloc[0]).strip()
    child = str(row.iloc[1]).strip()
    qty = pd.to_numeric(row.iloc[2], errors='coerce') or 1.0
    uom = str(row.iloc[3]).strip() if len(row) > 3 else "Ea."

    if parent not in bom_tree:
        bom_tree[parent] = []
    bom_tree[parent].append({'id': child, 'qty': qty, 'uom': uom})

# --- 4. NAVIGATION & SUB-ASSEMBLY SELECTION ---
st.sidebar.header("Navigation View")

# Offer Category SKUs if SKU file is present, otherwise show full Parent / Sub-Assembly list
nav_mode = st.sidebar.radio("View Depth Mode", ["Sub-Assemblies (All Parents)", "Top Level Category SKUs"])

selection = "-- Select --"

if nav_mode == "Sub-Assemblies (All Parents)":
    sub_options = []
    for p_id in sorted(bom_tree.keys()):
        p_desc = master_map.get(p_id, {}).get('Part Description', 'N/A')
        sub_options.append(f"{p_id} | {p_desc}")
    
    selection = st.selectbox("Select Sub-Assembly / Parent Part", ["-- Select --"] + sub_options)

else:
    if df_s is not None:
        cols = df_s.columns.tolist()
        cat_map = {
            "Saleable SKUs": ("Saleable Sku", "Saleable Sku Description"),
            "Base Assemblies": ("Base Assy Kit", "Base Assy Kit Description"),
            "Countertops": ("Countertop Assy Kit", "Countertop Assy Kit Description"),
            "Cladding": ("Cladding Assy Kit", "Cladding Assy Kit Description"),
            "Finish Kits": ("Finish Kit", "Finish Kit Description")
        }
        available_cats = [k for k, v in cat_map.items() if v[0] in cols]
        if available_cats:
            cat_choice = st.selectbox("Select Category", available_cats)
            id_col, desc_col = cat_map[cat_choice]
            
            sku_options = []
            valid_rows = df_s[df_s[id_col].notna() & (df_s[id_col] != "")]
            for _, r in valid_rows.drop_duplicates(subset=[id_col]).iterrows():
                sku_options.append(f"{r[id_col]} | {r.get(desc_col, 'N/A')}")
            selection = st.selectbox(f"Select {cat_choice}", ["-- Select --"] + sorted(sku_options))
        else:
            st.warning("SKU category structure not matched. Reverting to Sub-Assembly dropdown.")
            sub_options = [f"{p_id} | {master_map.get(p_id, {}).get('Part Description', 'N/A')}" for p_id in sorted(bom_tree.keys())]
            selection = st.selectbox("Select Sub-Assembly", ["-- Select --"] + sub_options)
    else:
        st.info("No L0/L1 SKU definition file found. Showing all Sub-Assemblies.")
        sub_options = [f"{p_id} | {master_map.get(p_id, {}).get('Part Description', 'N/A')}" for p_id in sorted(bom_tree.keys())]
        selection = st.selectbox("Select Sub-Assembly", ["-- Select --"] + sub_options)

# --- 5. WATERFALL CALCULATION & DISPLAY ENGINE ---
if selection != "-- Select --":
    sel_id = selection.split(" | ")[0].strip()
    sel_name = selection.split(" | ")[1].strip() if " | " in selection else "Assembly"

    final_bom = []
    def explode(pid, depth=1, mult=1):
        if depth > 12: return  # Guard against infinite recursion
        for child in bom_tree.get(pid, []):
            cid = child['id']
            t_qty = mult * child['qty']
            meta = master_map.get(cid, {})
            
            final_bom.append({
                'Level': depth,
                'Part No.': cid,
                'Description': meta.get('Part Description', 'N/A'),
                'Total Qty': t_qty,
                'UOM': child['uom'],
                'Unit Cost': meta.get('Math_Cost', 0.0),
                'Ext. Cost': meta.get('Math_Cost', 0.0) * t_qty
            })
            explode(cid, depth + 1, t_qty)

    explode(sel_id)

    if final_bom:
        res_df = pd.DataFrame(final_bom)
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Total Roll-up Cost", f"${res_df['Ext. Cost'].sum():,.2f}")
        col_m2.metric("Total Component Lines", f"{len(res_df)} items")
        
        # Display Table
        disp = res_df.copy()
        disp['Unit Cost'] = disp['Unit Cost'].map("${:,.2f}".format)
        disp['Ext. Cost'] = disp['Ext. Cost'].map("${:,.2f}".format)
        st.dataframe(disp, use_container_width=True, hide_index=True)
        
        # CSV Export with Single Cell Header ("Name, PartNo")
        csv_header = f'"{sel_name}, {sel_id}"\n\n'
        csv_body = res_df.to_csv(index=False)
        st.download_button(
            label=f"📥 Download {sel_id} Waterfall CSV",
            data=(csv_header + csv_body).encode('utf-8-sig'),
            file_name=f"BOM_{sel_id}.csv",
            mime="text/csv"
        )
    else:
        st.warning(f"No components found for '{sel_id}'. Ensure this assembly ID is present in the 'Parent Part' column of your BOM Links file.")