import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 載入 .env 檔案（如果在本地開發的話）
load_dotenv()

def test_gemini_connection():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ 錯誤: 找不到 GEMINI_API_KEY 環境變數。請確認你有在 .env 設定！")
        return

    print("✅ 找到 GEMINI_API_KEY，嘗試連線到 Gemini API...")
    try:
        # 初始化 Gemini Client
        client = genai.Client(api_key=api_key)
        
        # 測試呼叫模型
        response = client.models.generate_content(
            model='gemini-3.1-pro-preview', # 用最基本的模型測試連線
            contents='Hello! Please respond with a simple greeting.',
        )
        print("\n🎉 連線成功！Gemini API 的回應：")
        print("-" * 30)
        print(response.text)
        print("-" * 30)
    except Exception as e:
        print(f"\n❌ 連線失敗: {e}")

if __name__ == "__main__":
    test_gemini_connection()
