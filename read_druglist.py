import streamlit as st
import pandas as pd

# โหลดข้อมูลจากไฟล์ Excel
df = pd.read_excel("druglist.xlsx")

# เอารายชื่อยาแบบไม่ซ้ำ
drug_list = df["drug_name"].dropna().unique()

# สร้าง ComboBox ให้เลือกชื่อยา
selected_drug = st.selectbox("เลือกชื่อยา", drug_list)

# แสดงข้อมูลของยาที่เลือก
drug_info = df[df["drug_name"] == selected_drug]
st.write("ข้อมูลของยา:")
st.dataframe(drug_info)
