import streamlit as st
import pandas as pd
from io import BytesIO
import base64

st.set_page_config(page_title="Drug Finder", page_icon="💊", layout="centered")

# ========== ฟังก์ชันดาวน์โหลด Excel ==========
def to_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Drugs')
    b64 = base64.b64encode(output.getvalue()).decode()
    return f"""
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
    """

# ========== สีของแต่ละบัญชี ==========
def get_border_color(account_id):
    account_id = str(account_id).strip()
    color_map = {
        "ก": "#38bdf8",
        "ข": "#4ade80",
        "ค": "#facc15",
        "ง": "#fb923c",
        "จ": "#f472b6",
        "นอกบัญชี": "#a3a3a3",
        "บัญชียาจากสมุนไพร": "#7a3a1d",
    }
    return color_map.get(account_id, "#60a5fa")

# ========== โหลดข้อมูล ==========
df = pd.read_excel("druglist.xlsx")

# ========== หัวเรื่อง ==========
st.markdown('<h3 style="margin-bottom: 0; color: #6A1B9A;">💊 บัญชียา รพ.ท้ายเหมืองชัยพัฒน์ ปีงบ 2568</h3>', unsafe_allow_html=True)

# ========== CSS ==========
st.markdown("""
<style>
.drug-card {
    padding: 8px 14px;
    margin-bottom: 8px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 15px;
    background-color: #f0f9ff;
}
.group-box {
    padding: 12px;
    background-color: #ede9fe;
    border-left: 6px solid #6D28D9;
    border-radius: 6px;
    margin-top: 16px;
    margin-bottom: 8px;
}
.subgroup-title {
    margin-top: 12px;
    font-weight: bold;
    color: #4B0082;
}
</style>
""", unsafe_allow_html=True)

# ========== ตัวกรอง ==========
if st.button("🔄 เคลียร์ตัวกรองทั้งหมด"):
    st.session_state["subtype1_filter"] = "--ทั้งหมด--"
    st.session_state["subtype2_filter"] = "--ทั้งหมด--"
    st.session_state["account_filter"] = "--ทั้งหมด--"
    st.session_state["search_text"] = ""
    st.session_state["sort_mode"] = "เรียงตามชื่อยา"

sort_mode = st.radio("🧭 เรียงข้อมูลโดย", ["เรียงตามชื่อยา", "เรียงตามกลุ่มยา"], key="sort_mode", horizontal=True)

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

# 🔽 ปุ่มดาวน์โหลด Excel (ด้านบน)
st.markdown(to_excel_download(df), unsafe_allow_html=True)

# ========== แสดงผล ==========
st.caption(f"🎯 ตัวกรอง: {selected_subtype1} > {selected_subtype2} > {selected_account} | ค้นหา: {search_text if search_text else '-'}")

if sort_mode == "เรียงตามชื่อยา":
    unique_drugs = df["drug_name"].dropna().unique()
    st.subheader(f"📋 พบ {len(unique_drugs)} รายการชื่อยาไม่ซ้ำ")

    if len(unique_drugs) == 0:
        st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไข")
    else:
        for drug in unique_drugs:
            entries = df[df["drug_name"] == drug]
            if len(entries) == 1:
                row = entries.iloc[0]
                color = get_border_color(row['account_drug_ID'])
                st.markdown(f"""
                <div class="drug-card" style="border-left: 6px solid {color};">
                    <strong>{row['drug_name']}</strong><br>
                    <span style="color: #555;">บัญชี: {row['account_drug_ID']}</span><br>
                    <span style="color: #666;">กลุ่ม: {row['subtype1_name']} > {row['subtype2_name']} > {row['subtype3_name']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                with st.expander(f"💊 {drug} ({len(entries)} กลุ่มยา)"):
                    for _, row in entries.iterrows():
                        color = get_border_color(row['account_drug_ID'])
                        st.markdown(f"""
                        <div class="drug-card" style="border-left: 6px solid {color};">
                            <strong>{row['drug_name']}</strong><br>
                            <span style="color: #555;">บัญชี: {row['account_drug_ID']}</span><br>
                            <span style="color: #666;">กลุ่ม: {row['subtype1_name']} > {row['subtype2_name']} > {row['subtype3_name']}</span>
                        </div>
                        """, unsafe_allow_html=True)
else:
    st.subheader("🧪 เรียงตามกลุ่มยา")
    grouped = df.groupby("subtype1_name")

for subtype1, group1 in grouped:
    st.markdown(f"<h4 style='margin-top:30px;color:#4B0082;'>{subtype1}</h4>", unsafe_allow_html=True)

    sub2_grouped = group1.groupby("subtype2_name")
    for subtype2, group2 in sub2_grouped:
        if not pd.isna(subtype2):
            st.markdown(f"<h5 style='margin-top:16px;color:#6A1B9A;'>&nbsp;&nbsp;• {subtype2}</h5>", unsafe_allow_html=True)

        sub3_grouped = group2.groupby("subtype3_name")
        for subtype3, group3 in sub3_grouped:
            if not pd.isna(subtype3):
                st.markdown(f"<div style='margin-left:24px;margin-bottom:6px;font-weight:bold;color:#9C27B0;'>⇨ {subtype3}</div>", unsafe_allow_html=True)

            for _, row in group3.iterrows():
                name = row["drug_name"]
                account = row["account_drug_ID"]
                color = get_border_color(account)
                st.markdown(f"""
                <div class="drug-card" style="border-left: 8px solid {color}; margin-left: 32px;">
                    {name} <span style="color: gray;">({account})</span>
                </div>
                """, unsafe_allow_html=True)

# 🔽 ปุ่มดาวน์โหลด Excel (ด้านล่าง)
st.markdown(to_excel_download(df), unsafe_allow_html=True)

# ========== Footer ==========
st.markdown("---")
st.caption("จัดทำโดย กลุ่มงานเภสัชกรรม รพ.ท้ายเหมืองชัยพัฒน์ | © 2568")
