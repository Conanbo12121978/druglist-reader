import streamlit as st
import pandas as pd

# โหลดไฟล์ Excel
df = pd.read_excel("druglist.xlsx")

# แสดงตารางข้อมูลทั้งหมด
st.subheader("📋 รายการยาทั้งหมด")
st.dataframe(df)

# ---------- ฟิลเตอร์ประเภท ----------
st.subheader("🔎 ตัวกรองข้อมูล")

# สร้างตัวเลือกสำหรับ subtype1_name
subtype_options = df["subtype1_name"].dropna().unique()
selected_subtype = st.selectbox("เลือกประเภท (subtype1_name)", ["ทั้งหมด"] + list(subtype_options))

# กรองตามประเภทก่อน (ถ้าเลือก)
if selected_subtype != "ทั้งหมด":
    df = df[df["subtype1_name"] == selected_subtype]

# ---------- ฟิลเตอร์ชื่อยา ----------
# ดึงชื่อยาจากข้อมูลที่ถูกกรองตาม subtype แล้ว
drug_options = df["drug_name"].dropna().unique()
selected_drug = st.selectbox("เลือกชื่อยา", ["ทั้งหมด"] + list(drug_options))

# กรองตามชื่อยา (ถ้าเลือก)
if selected_drug != "ทั้งหมด":
    df = df[df["drug_name"] == selected_drug]

# ---------- แสดงผลลัพธ์ ----------
st.subheader("🧾 ข้อมูลที่กรองแล้ว")
st.dataframe(df)
