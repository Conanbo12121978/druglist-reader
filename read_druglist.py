import streamlit as st
import pandas as pd
from io import BytesIO
import base64

st.set_page_config(page_title="Drug Finder", page_icon="💊", layout="centered")

# 📦 โหลดข้อมูล
df = pd.read_excel("druglist.xlsx")
df["account_drug_ID"] = df["account_drug_ID"].fillna("").astype(str).str.strip()

# 🎨 สีเส้นตามบัญชี
def get_border_color(account_id):
    account_id = str(account_id).strip()
    color_map = {
        "ก": "#38bdf8", "ข": "#4ade80", "ค": "#facc15", "ง": "#fb923c",
        "จ": "#f472b6", "นอกบัญชี": "#a3a3a3", "บัญชียาจากสมุนไพร": "#7a3a1d"
    }
    return color_map.get(account_id, "#60a5fa")

# 📥 ฟังก์ชันดาวน์โหลด
def to_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Drugs')
    b64 = base64.b64encode(output.getvalue()).decode()
    return f'''
        <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}"
           download="filtered_drugs.xlsx" style="text-decoration: none; background-color: #2563eb; color: white;
           padding: 8px 16px; border-radius: 6px; display: inline-block; margin-top: 10px;">
           📥 ดาวน์โหลด Excel
        </a>
    '''

# 🟣 หัวเรื่อง
st.markdown('<h3 style="color: #6A1B9A;">💊 บัญชียา รพ.ท้ายเหมืองชัยพัฒน์ ปีงบ 2568</h3>', unsafe_allow_html=True)

# 🔘 ตัวกรอง
if st.button("🔄 เคลียร์ตัวกรองทั้งหมด"):
    st.session_state["subtype1_filter"] = "--ทั้งหมด--"
    st.session_state["subtype2_filter"] = "--ทั้งหมด--"
    st.session_state["account_filter"] = "--ทั้งหมด--"
    st.session_state["search_text"] = ""

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

# 🔽 ดาวน์โหลดด้านบน
st.markdown(to_excel_download(df), unsafe_allow_html=True)

# 🔢 เรียงตามชื่อยา / กลุ่มยา
sort_mode = st.radio("📚 เรียงข้อมูลตาม", ["ชื่อยา (A-Z)", "กลุ่มยา"], horizontal=True)

# 🧾 แสดงผลลัพธ์
st.caption(f"🎯 ตัวกรอง: {selected_subtype1} > {selected_subtype2} > {selected_account} | ค้นหา: {search_text if search_text else '-'}")
st.subheader(f"📋 พบ {df['drug_name'].nunique()} รายการชื่อยาไม่ซ้ำ")

if df.empty:
    st.warning("ไม่พบข้อมูลที่ตรงกับเงื่อนไข")
else:
    if sort_mode == "ชื่อยา (A-Z)":
        df_sorted = df.sort_values(by=["drug_name"])
        for drug in df_sorted["drug_name"].dropna().unique():
            entries = df_sorted[df_sorted["drug_name"] == drug]
            with st.expander(f"💊 {drug} ({len(entries)} กลุ่มยา)"):
                for _, row in entries.iterrows():
                    color = get_border_color(row["account_drug_ID"])
                    group_info = " > ".join([
                        str(row.get("subtype1_name", "")).strip(),
                        str(row.get("subtype2_name", "")).strip(),
                        str(row.get("subtype3_name", "")).strip()
                    ])
                    group_info = group_info.replace("> nan", "").replace("nan", "")
                    st.markdown(f"""
                    <div style="border-left: 8px solid {color}; padding: 10px; margin-bottom: 10px; background-color: #f0f9ff; border-radius: 8px;">
                        <strong>บัญชี:</strong> {row['account_drug_ID']}<br>
                        <strong>กลุ่มยา:</strong> {group_info if group_info.strip() else 'ไม่ระบุ'}
                    </div>
                    """, unsafe_allow_html=True)

    else:
        # เรียงตามกลุ่ม + บัญชี + ชื่อยา
        df_sorted = df.copy()
        df_sorted["account_sort"] = df_sorted["account_drug_ID"].replace("", "Ω")  # ค่าว่างไว้ท้าย
        df_sorted = df_sorted.sort_values(by=[
            "subtype1_name", "subtype2_name", "subtype3_name", "account_sort", "drug_name"
        ])

        for subtype1, df1 in df_sorted.groupby("subtype1_name"):
            st.markdown(f"<h5 style='margin-top: 30px; color:#4C1D95;'>🧪 {subtype1}</h5>", unsafe_allow_html=True)
            for subtype2, df2 in df1.groupby("subtype2_name"):
                for subtype3, df3 in df2.groupby("subtype3_name"):
                    group_label = " > ".join([x for x in [subtype2, subtype3] if pd.notna(x) and x.strip()])
                    if group_label:
                        st.markdown(f"<h6 style='margin-top: 10px; margin-bottom: 4px;'>{group_label}</h6>", unsafe_allow_html=True)

                    for _, row in df3.iterrows():
                        color = get_border_color(row["account_drug_ID"])
                        st.markdown(f"""
                        <div style="border-left: 8px solid {color}; padding: 8px 12px; margin-bottom: 8px; background-color: #f0f9ff; border-radius: 6px;">
                            <strong>{row["drug_name"]}</strong> ({row["account_drug_ID"]})
                        </div>
                        """, unsafe_allow_html=True)

# 📥 ปุ่มดาวน์โหลดด้านล่าง
st.markdown(to_excel_download(df), unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("จัดทำโดย กลุ่มงานเภสัชกรรม รพ.ท้ายเหมืองชัยพัฒน์ | © 2568")
