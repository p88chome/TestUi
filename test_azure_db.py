"""
快速測試 Azure PostgreSQL 連線
用法: python test_azure_db.py
"""
import psycopg2
import sys

# ============================
# 填入你的 Azure DB 資訊
# ============================
HOST     = "allai.postgres.database.azure.com"
PORT     = 5432
DATABASE = "postgres"
USER     = "admin_luis"
PASSWORD = "Pppp8768."   # ← 改這裡
# ============================

print(f"🔌 正在連線到 {HOST}:{PORT}/{DATABASE} ...")
print(f"   使用者: {USER}")

try:
    cnx = psycopg2.connect(
        host=HOST,
        port=PORT,
        database=DATABASE,
        user=USER,
        password=PASSWORD,
        sslmode="require",
        connect_timeout=10
    )
    cursor = cnx.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"\n✅ 連線成功！")
    print(f"   PostgreSQL 版本: {version[0]}")

    cursor.execute("SELECT current_database(), current_user;")
    db, user = cursor.fetchone()
    print(f"   目前資料庫: {db}")
    print(f"   目前使用者: {user}")

    cursor.close()
    cnx.close()
    print("\n🎉 測試完成，資料庫連線正常！可以部署了。")
    sys.exit(0)

except psycopg2.OperationalError as e:
    print(f"\n❌ 連線失敗！")
    print(f"   錯誤訊息: {e}")
    print("\n💡 常見原因：")
    print("   1. 密碼錯誤")
    print("   2. 防火牆沒開放您的 IP（Azure Portal → PostgreSQL → 網路功能）")
    print("   3. sslmode 問題")
    sys.exit(1)
