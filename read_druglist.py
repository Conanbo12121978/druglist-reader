import streamlit as st
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

# ========== โหลดข้อมูล ==========
df = pd.read_excel("druglist.xlsx")

# ========== Page Config ==========
st.set_page_config(page_title="Drug Finder", page_icon="💊", layout="centered")
st.markdown('<h3 style="margin-bottom: 0; color: #6A1B9A;">💊 บัญชียา รพ.ท้ายเหมืองชัยพัฒน์ ปีงบ 2568</h3>', unsafe_allow_html=True)

# ========== CSS Style ==========
st.markdown("""
<style>
/* 💊 กล่องแสดงรายการยา */
.drug-card {
    padding: 12px 16px;
    margin-bottom: 12px;
    border-left: 6px solid #38bdf8;
    border-radius: 8px;
    font-size: 16px;
    transition: background-color 0.3s ease, color 0.3s ease;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

/* 🌞 โหมดสว่าง */
@media (prefers-color-scheme: light) {
    .drug-card {
        background-color: #f0f9ff;
        color: #000000;
    }
}

/* 🌚 โหมดมืด */
@media (prefers-color-scheme: dark) {
    .drug-card {
        background-color: #2a2e3b;  /* ปรับให้สว่างกว่าสีดำ */
        color: #ffffff;
    }
}

/* 🔗 ลิงก์ปุ่มดาวน์โหลด */
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

/* ปรับสีพื้นหลัง dropdown ของ selectbox */
div[data-baseweb="select"] > div {
    background-color: #2d3748;  /* พื้นหลัง dropdown */
    color: white;
}

/* เมื่อ hover รายการ */
div[data-baseweb="select"] div:hover {
    background-color: #4c566a;
}

/* สีเมื่อรายการถูกเลือก */
div[data-baseweb="select"] div[aria-selected="true"] {
    background-color: #6a1b9a !important;  /* สีม่วง */
    color: white;
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

# ========== แสดงจำนวนและผลลัพธ์ ==========
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
            group_parts = [
                str(row.get("subtype1_name", "")).strip(),
                str(row.get("subtype2_name", "")).strip(),
                str(row.get("subtype3_name", "")).strip()
            ]
            group_info = " > ".join([g for g in group_parts if g and g.lower() != "nan"])

            st.markdown(f"""
            <div class="drug-card">
                <strong>ชื่อยา:</strong> {row['drug_name']}<br>
                <strong>บัญชี:</strong> {row['account_drug_ID']}<br>
                <strong>กลุ่มยา:</strong> {group_info if group_info else 'ไม่ระบุ'}
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.expander(f"{drug} ({len(entries)} กลุ่มยา)"):
                for _, row in entries.iterrows():
                    group_parts = [
                        str(row.get("subtype1_name", "")).strip(),
                        str(row.get("subtype2_name", "")).strip(),
                        str(row.get("subtype3_name", "")).strip()
                    ]
                    group_info = " > ".join([g for g in group_parts if g and g.lower() != "nan"])

                    st.markdown(f"""
                    <div class="drug-card">
                        <strong>บัญชี:</strong> {row['account_drug_ID']}<br>
                        <strong>กลุ่มยา:</strong> {group_info if group_info else 'ไม่ระบุ'}
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown(to_excel_download(df), unsafe_allow_html=True)

# ========== Footer ==========
st.markdown("---")
st.caption("จัดทำโดย กลุ่มงานเภสัชกรรม รพ.ท้ายเหมืองชัยพัฒน์ | © 2568")
