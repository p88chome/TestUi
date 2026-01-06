import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.domain import Component, EndpointType

def seed_components():
    db = SessionLocal()
    
    # The new granular 'LEGO' components (Traditional Chinese)
    # logic: Try to find by English name first (for upgrade), then Chinese.
    new_components = [
        # Input
        {"id_key": "ocr", "name": "全能 OCR", "name_en": "Universal OCR", "description": "通用文件辨識 (PDF/Image)", "endpoint_type": EndpointType.CLOUD_LLM, "tags": ["input", "vision"]},
        
        # Fundamental Functional Blocks
        {"id_key": "splitter", "name": "條款拆解器", "name_en": "Clause Splitter", "description": "將法律文本拆解為獨立條款", "endpoint_type": EndpointType.RULE_ENGINE, "tags": ["legal", "nlp"]},
        {"id_key": "fetcher", "name": "數據撈取器", "name_en": "Data Fetcher", "description": "從資料庫或 API 獲取數據", "endpoint_type": EndpointType.ETL_ADAPTER, "tags": ["data", "integration"]},
        
        # AI/Logic Engines
        {"id_key": "risk", "name": "風險掃描 (Risk Scanner)", "name_en": "Risk Scanner", "description": "偵測高風險條款 (AI + 規則)", "endpoint_type": EndpointType.CLOUD_LLM, "tags": ["legal", "risk"]},
        {"id_key": "rules", "name": "規則引擎 (Rule Engine)", "name_en": "Rule Engine", "description": "執行預定義的業務邏輯", "endpoint_type": EndpointType.RULE_ENGINE, "tags": ["logic", "compliance"]},
        {"id_key": "diff", "name": "差異比對引擎", "name_en": "Diff Engine", "description": "比對兩個版本的文本差異", "endpoint_type": EndpointType.RULE_ENGINE, "tags": ["utility", "comparison"]},
        {"id_key": "intent", "name": "意圖識別路由", "name_en": "Intent Router", "description": "識別用戶意圖並分流", "endpoint_type": EndpointType.CLOUD_LLM, "tags": ["ai", "routing"]},
        
        # Output
        {"id_key": "doc_gen", "name": "報告生成器", "name_en": "Doc Formatter", "description": "生成格式化的 .docx/.pdf 報告", "endpoint_type": EndpointType.ETL_ADAPTER, "tags": ["output", "report"]},
        
        # Manufacturing / Industrial
        {"id_key": "sop_qa", "name": "SOP 檢索助手 (RAG)", "name_en": "SOP Retriever (RAG)", "description": "從 SOP 與手冊中回答問題", "endpoint_type": EndpointType.CLOUD_LLM, "tags": ["manufacturing", "qa"]},
        {"id_key": "safety", "name": "工安合規檢查", "name_en": "Safety Validator", "description": "檢查動作是否符合 ISO/OSHA 規範", "endpoint_type": EndpointType.RULE_ENGINE, "tags": ["manufacturing", "safety"]},
    ]

    print("Seeding Components...")
    try:
        for comp_data in new_components:
            # 1. Check if already exists in Chinese
            start_zh = db.query(Component).filter(Component.name == comp_data["name"]).first()
            
            # 2. Check if exists in English (Legacy)
            start_en = None
            if not start_zh and "name_en" in comp_data:
                 start_en = db.query(Component).filter(Component.name == comp_data["name_en"]).first()

            if start_zh:
                print(f"Skipped (Exists): {comp_data['name']}")
                
            elif start_en:
                print(f"Updating English -> Chinese: {start_en.name} -> {comp_data['name']}")
                start_en.name = comp_data["name"]
                start_en.description = comp_data["description"]
                start_en.endpoint_type = comp_data["endpoint_type"]
                start_en.tags = comp_data["tags"]
                db.add(start_en)
                
            else:
                comp = Component(
                    name=comp_data["name"],
                    description=comp_data["description"],
                    endpoint_type=comp_data["endpoint_type"],
                    tags=comp_data["tags"],
                    input_schema={},
                    output_schema={}
                )
                db.add(comp)
                print(f"Added: {comp_data['name']}")
        
        db.commit()
        print("Seeding Complete!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_components()
