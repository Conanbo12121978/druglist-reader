import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# ฟังก์ชันสำหรับ export เป็น Excel
def to_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Drugs')
    processed_data = output.getvalue()
    b64 = base64.b64encode(processed_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="filtered_drugs.xlsx">📥 ดาวน์โหลด Excel</a>'
    return href

# โหลดข้อมูล
df = pd.read_excel("druglist.xlsx")

st.title("💊 ค้นหารายชื่อยา")

# ========== ตัวกรองประเภทหลัก ==========
subtype1_list = df["subtype1_name"].dropna().unique()
selected_subtype1 = st.selectbox("เลือกประเภทหลัก (subtype1_name)", ["ทั้งหมด"] + list(subtype1_list))
if selected_subtype1 != "ทั้งหมด":
    df = df[df["subtype1_name"] == selected_subtype1]

# ========== ตัวกรองประเภทย่อย ==========
subtype2_list = df["subtype2_name"].dropna().unique()
selected_subtype2 = st.selectbox("เลือกประเภทรอง (subtype2_name)", ["ทั้งหมด"] + list(subtype2_list))
if selected_subtype2 != "ทั้งหมด":
    df = df[df["subtype2_name"] == selected_subtype2]

# ========== ช่องค้นหาชื่อยา ==========
search_text = st.text_input("🔎 พิมพ์ชื่อยาที่ต้องการค้นหา (drug_name)")

if search_text:
    df = df[df["drug_name"].str.contains(search_text, case=False, na=False)]

# ========== แสดงผลแบบข้อความ ==========
st.subheader("📋 รายชื่อยาที่ค้นพบ")

if df.empty:
    st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไข")
else:
    for index, row in df.iterrows():
        st.markdown(f"""
        <div style="background-color: #f9f9f9; padding: 10px; margin-bottom: 10px; border-left: 5px solid #4CAF50;">
        <strong>ชื่อยา:</strong> {row['drug_name']}<br>
        <strong>รหัสบัญชียา:</strong> {row['account_drug_ID']}
        </div>
        """, unsafe_allow_html=True)

    # ========== ปุ่มดาวน์โหลด Excel ==========
    st.markdown("---")
    st.markdown(to_excel_download(df), unsafe_allow_html=True)
