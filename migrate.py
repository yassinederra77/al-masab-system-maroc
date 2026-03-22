import sqlite3
import libsql_client as libsql
import pandas as pd
import asyncio

# 1. إعداد البيانات (نفس الروابط السابقة)
TURSO_URL = "libsql://al-masab-db-yassinederra77.aws-eu-west-1.turso.io"
TURSO_TOKEN = "EyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzQxMzIzNzYsImlkIjoiMDE5ZDEyODctODQwMS03ZTdhLWI4ODgtMTI2YmM3YjU1YTRiIiwicmlkIjoiOGVmYzQzOWMtZjAzMS00NWQwLWJhZTItMzRiOTRiNWMwNjZiIn0.mXHyH939WTc_dFjg82Z9Ur8zl5azWacapBWgjgv7A5w2lM7U6OAoH4IIMgWHNg861lvSDxIWOHfCbRidZ90aDQ"

async def migrate():
    # الاتصال بالقاعدة المحلية (SQLite)
    local_conn = sqlite3.connect('school_data.db')
    
    # الاتصال بالقاعدة السحابية (Turso) باستخدام create_client_sync أو العميل الحديث
    remote_client = libsql.create_client_sync(url=TURSO_URL, auth_token=TURSO_TOKEN)

    tables = ['users', 'classes', 'students', 'attendance']
    
    for table in tables:
        print(f"🔄 جاري نقل جدول: {table}...")
        try:
            # قراءة البيانات من الملف المحلي
            df = pd.read_sql_query(f"SELECT * FROM {table}", local_conn)
            
            if not df.empty:
                # تحويل البيانات إلى صيغة يفهمها السحاب
                for _, row in df.iterrows():
                    placeholders = ", ".join(["?"] * len(row))
                    columns = ", ".join(df.columns)
                    values = tuple(row)
                    
                    query = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"
                    remote_client.execute(query, values)
                
                print(f"✅ تم نقل {len(df)} سطر في جدول {table}.")
            else:
                print(f"ℹ️ الجدول {table} فارغ.")
        except Exception as e:
            print(f"❌ خطأ في جدول {table}: {e}")

    print("\n🚀 مبروك! كل البيانات الآن في السحاب.")

if __name__ == "__main__":
    asyncio.run(migrate())