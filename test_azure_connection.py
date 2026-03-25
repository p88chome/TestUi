import os
import httpx
from dotenv import load_dotenv

def test_azure_connection():
    # 載入 .env 檔案
    load_dotenv()
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    
    print("=== Azure OpenAI 連線測試 ===")
    print(f"Endpoint: {endpoint}")
    print(f"Deployment 名稱: {deployment}")
    print(f"API 版本: {api_version}")
    print(f"API_KEY 長度: {len(api_key) if api_key else 0} 字元")
    print("=============================")
    
    if not endpoint or not api_key:
        print("❌ 錯誤：.env 檔案中缺少 AZURE_OPENAI_ENDPOINT 或 AZURE_OPENAI_API_KEY")
        return
        
    # 組裝 Azure OpenAI 請求 URL
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    payload = {
        "messages": [
            {"role": "user", "content": "測試連線，請回覆'連線成功'"}
        ],
        "max_tokens": 50
    }
    
    print(f"\n🔗 發送請求至: {url}")
    
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(url, headers=headers, json=payload)
            print(f"\n🎯 狀態碼 (Status Code): {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 連線成功！API 金鑰和端點皆正確。")
                print("回覆內容:")
                print(response.json()["choices"][0]["message"]["content"])
            elif response.status_code == 403:
                print("❌ 錯誤 403 Forbidden (權限不足)")
                print("可能原因：")
                print("1. API Key 不正確")
                print("2. 該 API Key 無法存取這個 Endpoint")
                print("3. Azure 防火牆擋住了您的 IP")
                print(f"詳細錯誤: {response.text}")
            elif response.status_code == 404:
                print("❌ 錯誤 404 Not Found (找不到資源)")
                print("可能原因：")
                print(f"1. 您的模型 Deployment Name ('{deployment}') 拼寫錯誤，或者該資源尚未建立此部署。")
                print("2. API Version 錯誤。")
                print(f"詳細錯誤: {response.text}")
            else:
                print("❌ 請求失敗。")
                print(f"詳細錯誤: {response.text}")
    except Exception as e:
        print(f"💥 發生例外錯誤: {e}")

if __name__ == "__main__":
    test_azure_connection()
