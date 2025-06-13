import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# ========= ฟังก์ชันสำหรับสร้างลิงก์ดาวน์โหลด Excel =========
def to_excel_download(df):
    output = BytesIO()
    # ✅ ใช้ openpyxl แทน xlsxwriter เพื่อหลีกเลี่ยง error
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Drugs')
    processed_data = output.getvalue()
    b64 = base64.b64encode(processed_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="filtered_drugs.xlsx">📥 ดาวน์โหลด Excel</a>'
    return href

# ========= โหลดข้อมูล =========
df = pd.read_excel("druglist.xlsx")

st.title("💊 ระบบค้นหาข้อมูลยา")

# ========= ตัวกรอง subtype1_name =========
subtype1_list = df["subtype1_name"].dropna().unique()
selected_subtype1 = st.selectbox("เลือกประเภทหลัก (subtype1_name)", ["ทั้งหมด"] + sorted(list(subtype1_list)))
if selected_subtype1 != "ทั้งหมด":
    df = df[df["subtype1_name"] == selected_subtype1]

# ========= ตัวกรอง subtype2_name =========
subtype2_list = df["subtype2_name"].dropna().unique()
selected_subtype2 = st.selectbox("เลือกประเภทรอง (subtype2_name)", ["ทั้งหมด"] + sorted(list(subtype2_list)))
if selected_subtype2 != "ทั้งหมด":
    df = df[df["subtype2_name"] == selected_subtype2]

# ========= ช่องค้นหา drug_name =========
search_text = st.text_input("🔎 พิมพ์ชื่อยา (drug_name)")
if search_text.strip():
    df = df[df["drug_name"].fillna("").str.contains(search_text, case=False)]

# ========= แสดงผล =========
st.subheader(f"📋 พบ {len(df)} รายการที่ตรงกับเงื่อนไข")

if df.empty:
    st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไขที่เลือก")
else:
    for _, row in df.iterrows():
        st.markdown(f"""
        <div style="background-color: #f0f9ff; padding: 10px; margin-bottom: 10px; border-left: 5px solid #3498db;">
        <strong>ชื่อยา:</strong> {row['drug_name']}<br>
        <strong>รหัสบัญชียา:</strong> {row['account_drug_ID']}
        </div>
        """, unsafe_allow_html=True)

    # ========= ลิงก์ดาวน์โหลด Excel =========
    st.markdown("---")
    st.markdown(to_excel_download(df), unsafe_allow_html=True)
