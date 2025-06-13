import pandas as pd

# อ่านไฟล์ Excel ที่อยู่ในโฟลเดอร์ data/
df = pd.read_excel('data/druglist.xlsx')

# แสดงข้อมูล 5 แถวแรก
print(df.head())
