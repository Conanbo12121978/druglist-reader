import streamlit as st

# 🔧 ต้องอยู่บนสุด!
st.set_page_config(page_title="Drug Finder", page_icon="💊", layout="centered")

import pandas as pd
from io import BytesIO
import base64

# ========== ฟังก์ชันดาวน์โหลด Excel ==========
def to_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Drugs')
    b64 = base64.b64encode(output.getvalue()).decode()
    return f'''
    <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" 
       download="filtered_drugs.xlsx" style="
       text-decoration: none;
       background-color: #2563eb;
       color: white;
       padding: 8px 16px;
       border-radius: 6px;
       display: inline-block;
       margin-top: 10px;
    ">
       📥 ดาวน์โหลด Excel
    </a>
    '''

# 🎨 ฟังก์ชันเลือกสีของแต่ละบัญชี
def get_border_color(account_id):
    account_id = str(account_id).strip()
    color_map = {
        "ก": "#38bdf8",       # ฟ้า
        "ข": "#4ade80",       # เขียวอ่อน
        "ค": "#facc15",       # เหลือง
        "ง": "#fb923c",       # ส้ม
        "จ": "#f472b6",       # ชมพู
        "นอกบัญชี": "#a3a3a3",  # เทา
        "บัญชียาจากสมุนไพร": "#7a3a1d",  # น้ำตาล
    }
    return color_map.get(account_id, "#60a5fa")  # ค่า default ถ้าไม่รู้จักบัญชี

# ========== โหลดข้อมูล ==========
df = pd.read_excel("druglist.xlsx")

# ========== หัวเรื่อง ==========
st.markdown('<h3 style="margin-bottom: 0; color: #6A1B9A;">💊 บัญชียา รพ.ท้ายเหมืองชัยพัฒน์ ปีงบ 2568</h3>', unsafe_allow_html=True)

# ========== CSS Style (พื้นฐาน) ==========
st.markdown("""
<style>
.drug-card {
    padding: 12px 16px;
    margin-bottom: 12px;
    border: 1px solid #60a5fa;
    border-radius: 8px;
    font-size: 16px;
    transition: background-color 0.3s ease, color 0.3s ease;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
@media (prefers-color-scheme: light) {
    .drug-card {
        background-color: #f0f9ff;
        color: #000000;
    }
}
@media (prefers-color-scheme: dark) {
    .drug-card {
        background-color: #f0f9ff;
        color: #000000;
    }
}
a {
    color: #ffffff;
    background-color: #2563eb;
    padding: 8px 16px;
    border-radius: 6px;
    display: inline-block;
    margin-top: 10px;
    text-decoration: none;
}
a:hover {
    background-color: #1e40af;
}
</style>
""", unsafe_allow_html=True)

# ========== ปุ่มเคลียร์ตัวกรอง ==========
if st.button("🔄 เคลียร์ตัวกรองทั้งหมด"):
    st.session_state["subtype1_filter"] = "--ทั้งหมด--"
    st.session_state["subtype2_filter"] = "--ทั้งหมด--"
    st.session_state["account_filter"] = "--ทั้งหมด--"
    st.session_state["search_text"] = ""

# ========== ตัวกรอง ==========
subtype1_list = df["subtype1_name"].dropna().unique()
selected_subtype1 = st.selectbox("เลือกประเภทหลัก", ["--ทั้งหมด--"] + sorted(subtype1_list), key="subtype1_filter")
if selected_subtype1 != "--ทั้งหมด--":
    df = df[df["subtype1_name"] == selected_subtype1]

subtype2_list = df["subtype2_name"].dropna().unique()
selected_subtype2 = st.selectbox("เลือกประเภทรอง", ["--ทั้งหมด--"] + sorted(subtype2_list), key="subtype2_filter")
if selected_subtype2 != "--ทั้งหมด--":
    df = df[df["subtype2_name"] == selected_subtype2]

account_list = df["account_drug_ID"].dropna().unique()
selected_account = st.selectbox("เลือกบัญชียา", ["--ทั้งหมด--"] + sorted(account_list), key="account_filter")
if selected_account != "--ทั้งหมด--":
    df = df[df["account_drug_ID"] == selected_account]

search_text = st.text_input("🔍 พิมพ์ชื่อยา", key="search_text")
if search_text.strip():
    df = df[df["drug_name"].fillna("").str.contains(search_text, case=False)]

# ========== แสดงผลลัพธ์ ==========
unique_drugs = df["drug_name"].dropna().unique()
st.caption(f"🎯 ตัวกรอง: {selected_subtype1} > {selected_subtype2} > {selected_account} | ค้นหา: {search_text if search_text else '-'}")
st.subheader(f"📋 พบ {len(unique_drugs)} รายการชื่อยาไม่ซ้ำ")

if len(unique_drugs) == 0:
    st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไข")
else:
    for drug in unique_drugs:
        entries = df[df["drug_name"] == drug]

        if len(entries) == 1:
            row = entries.iloc[0]
            account = row['account_drug_ID']
            color = get_border_color(account)
            group_parts = [
                str(row.get("subtype1_name", "")).strip(),
                str(row.get("subtype2_name", "")).strip(),
                str(row.get("subtype3_name", "")).strip()
            ]
            group_info = " > ".join([g for g in group_parts if g and g.lower() != "nan"])
            st.markdown(f"""
            <div class="drug-card" style="border-left: 8px solid {color};">
                <strong>ชื่อยา:</strong> {row['drug_name']}<br>
                <strong>บัญชี:</strong> {account}<br>
                <strong>กลุ่มยา:</strong> {group_info if group_info else 'ไม่ระบุ'}
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.expander(f"💊 {drug} ({len(entries)} กลุ่มยา)"):
                for _, row in entries.iterrows():
                    account = row['account_drug_ID']
                    color = get_border_color(account)
                    group_parts = [
                        str(row.get("subtype1_name", "")).strip(),
                        str(row.get("subtype2_name", "")).strip(),
                        str(row.get("subtype3_name", "")).strip()
                    ]
                    group_info = " > ".join([g for g in group_parts if g and g.lower() != "nan"])
                    st.markdown(f"""
                    <div class="drug-card" style="border-left: 8px solid {color};">
                        <strong>บัญชี:</strong> {account}<br>
                        <strong>กลุ่มยา:</strong> {group_info if group_info else 'ไม่ระบุ'}
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown(to_excel_download(df), unsafe_allow_html=True)

# ========== Footer ==========
st.markdown("---")
st.caption("จัดทำโดย กลุ่มงานเภสัชกรรม รพ.ท้ายเหมืองชัยพัฒน์ | © 2568")
