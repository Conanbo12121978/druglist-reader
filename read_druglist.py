import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# ========= ฟังก์ชันสำหรับดาวน์โหลด Excel =========
def to_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Drugs')
    processed_data = output.getvalue()
    b64 = base64.b64encode(processed_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="filtered_drugs.xlsx">📥 ดาวน์โหลด Excel</a>'
    return href

# ========= โหลดข้อมูล =========
df = pd.read_excel("druglist.xlsx")

st.set_page_config(page_title="Drug Finder", layout="centered")
st.title("💊 บัญชียา รพ.ท้ายเหมืองชัยพัฒน์ ปีงบ 68")

# ========= ปุ่มเคลียร์ตัวกรอง =========
if st.button("🔄 เคลียร์ตัวกรองทั้งหมด"):
    st.session_state["subtype1_filter"] = "ทั้งหมด"
    st.session_state["subtype2_filter"] = "ทั้งหมด"
    st.session_state["search_text"] = ""

# ========= ฟิลเตอร์ subtype1 =========
subtype1_list = df["subtype1_name"].dropna().unique()
selected_subtype1 = st.selectbox(
    "เลือกประเภทหลัก",
    ["ทั้งหมด"] + sorted(list(subtype1_list)),
    key="subtype1_filter"
)
if selected_subtype1 != "ทั้งหมด":
    df = df[df["subtype1_name"] == selected_subtype1]

# ========= ฟิลเตอร์ subtype2 =========
subtype2_list = df["subtype2_name"].dropna().unique()
selected_subtype2 = st.selectbox(
    "เลือกประเภทรอง",
    ["ทั้งหมด"] + sorted(list(subtype2_list)),
    key="subtype2_filter"
)
if selected_subtype2 != "ทั้งหมด":
    df = df[df["subtype2_name"] == selected_subtype2]

# ========= ช่องค้นหาชื่อยา =========
search_text = st.text_input("🔎 พิมพ์ชื่อยา", key="search_text")
if search_text.strip():
    df = df[df["drug_name"].fillna("").str.contains(search_text, case=False)]

# ========= แสดงผล =========
st.subheader(f"📋 พบ {len(df)} รายการที่ตรงกับเงื่อนไข")

if df.empty:
    st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไขที่เลือก")
else:
    for _, row in df.iterrows():
        st.markdown(f"""
        <div style="
            background-color: #1e293b;
            padding: 10px;
            margin-bottom: 10px;
            border-left: 5px solid #38bdf8;
            color: white;
            border-radius: 5px;
            font-size: 16px;
        ">
            <strong>ชื่อยา:</strong> {row['drug_name']}<br>
            <strong>บัญชียา:</strong> {row['account_drug_ID']}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(to_excel_download(df), unsafe_allow_html=True)
