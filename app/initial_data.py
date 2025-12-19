import logging
import sys
import os

# Add the parent directory to sys.path to allow running this script directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core import security
from app.models.user import User
from app.models.domain import AIModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    # ... existing user creation ...
    user = db.query(User).filter(User.email == "admin@example.com").first()
    if not user:
        user = User(
            email="admin@example.com",
            hashed_password=security.get_password_hash("admin"),
            full_name="Admin User",
            is_superuser=True,
            is_active=True,
        )
        db.add(user)
        db.commit()
        logger.info("Admin user created")
    else:
        user.hashed_password = security.get_password_hash("admin")
        db.add(user)
        db.commit()

    # Seed AI Models
    models_data = [
        {"name": "GPT-4.1", "deployment_name": "gpt-4.1", "api_version": "2024-12-01-preview", "is_active": True},
    ]

    for m in models_data:
        existing = db.query(AIModel).filter(AIModel.deployment_name == m["deployment_name"]).first()
        if not existing:
            db.add(AIModel(**m))
            logger.info(f"Seeded Model: {m['name']}")
    
    db.commit()

    # Seed Components
    from app.models.domain import Component, EndpointType
    
    # 1. AIOCR
    aiocr = db.query(Component).filter(Component.name == "AIOCR Component").first()
    if not aiocr:
        aiocr = Component(
            name="AIOCR Component",
            description="Calls Local OCR API Service (Python)",
            input_schema={"image_path": "string"},
            output_schema={"ocr_data": "dict"},
            tags=["ocr"],
            endpoint_type=EndpointType.CLOUD_LLM, 
            configuration={
                "kind": "ocr_api", 
                "url": "http://localhost:5000/api/ocr"
            }
        )
        db.add(aiocr)
        logger.info("AIOCR Component seeded")
    else:
        # Force update to ensure new logic applies
        aiocr.description = "Calls Internal OCR API (Azure Vision)"
        aiocr.input_schema = {"image_path": "string"}
        aiocr.output_schema = {"full_text": "string", "lines": "list"}
        aiocr.configuration = {
            "kind": "ocr_api", 
            # Point to local internal API
            # Note: WorkflowEngine doing 'httpx.post' to localhost:8000 might have Docker networking issues if in docker.
            # But user is on Windows local, so localhost:8000 is fine.
            "url": "http://localhost:8000/api/v1/ocr/analyze"
        }
        db.add(aiocr)
        logger.info("AIOCR Component updated to Internal OCR API")
    
    # 2. Expense Helper (Real AI)
    expense_helper = db.query(Component).filter(Component.name == "Expense Helper").first()
    if not expense_helper:
        expense_helper = Component(
            name="Expense Helper",
            description="AI Assistant for processing expense receipts and invoices.",
            input_schema={"full_text": "string"},
            output_schema={"analysis": "string"},
            tags=["expense", "ai", "finance"],
            endpoint_type=EndpointType.CLOUD_LLM,
            configuration={
                "kind": "azure_openai",
                "system_prompt": "You are a helpful finance assistant. Your task is to extract expense details from the provided OCR text (JSON format). Identify the Merchant, Date, Total Amount, and Category. Return the result as a concise summary.",
                "temperature": 0.3
            }
        )
        db.add(expense_helper)
        logger.info("Expense Helper seeded")
    else:
        # Force Upgrade to Real AI
        expense_helper.description = "AI Assistant for processing expense receipts and invoices."
        expense_helper.input_schema = {"full_text": "string"}
        expense_helper.endpoint_type = EndpointType.CLOUD_LLM
        expense_helper.configuration = {
            "kind": "azure_openai",
            "system_prompt": "You are a helpful finance assistant. Your task is to extract expense details from the provided OCR text (JSON format). Identify the Merchant, Date, Total Amount, and Category. Return the result as a concise summary.",
            "temperature": 0.3
        }
        db.add(expense_helper)
        logger.info("Expense Helper updated to Real AI")

        
    # 3. Contract Helper (Real AI)
    contract_helper = db.query(Component).filter(Component.name == "Contract Helper").first()
    if not contract_helper:
        contract_helper = Component(
            name="Contract Helper",
            description="AI Legal Expert for analyzing contracts.",
            input_schema={"full_text": "string"},
            output_schema={"analysis": "string"},
            tags=["contract", "ai", "legal"],
            endpoint_type=EndpointType.CLOUD_LLM,
            configuration={
                "kind": "azure_openai",
                "system_prompt": "You are an expert legal aide. Analyze the contract text provided in the OCR output (JSON). Identify the Parties, Effective Date, Key Terms, and any Risk Clauses. Provide a structured risk assessment.",
                "temperature": 0.5
            }
        )
        db.add(contract_helper)
        logger.info("Contract Helper seeded")
    else:
        # Force Upgrade to Real AI
        contract_helper.description = "AI Legal Expert for analyzing contracts."
        contract_helper.input_schema = {"full_text": "string"}
        contract_helper.endpoint_type = EndpointType.CLOUD_LLM
        contract_helper.configuration = {
            "kind": "azure_openai",
            "system_prompt": "You are an expert legal aide. Analyze the contract text provided in the OCR output (JSON). Identify the Parties, Effective Date, Key Terms, and any Risk Clauses. Provide a structured risk assessment.",
            "temperature": 0.5
        }
        db.add(contract_helper)
        logger.info("Contract Helper updated to Real AI")
    
    # 4. Universal Azure LLM
    azure_llm = db.query(Component).filter(Component.name == "Universal Azure LLM").first()
    if not azure_llm:
        azure_llm = Component(
            name="Universal Azure LLM",
            description="Calls Azure OpenAI using the active model or specified model_id.",
            input_schema={"prompt": "string", "messages": "list"},
            output_schema={"choices": "list", "usage": "dict"},
            tags=["llm", "azure"],
            endpoint_type=EndpointType.CLOUD_LLM,
            configuration={
                "kind": "azure_openai",
                "system_prompt": "You are a helpful AI assistant.",
                "temperature": 0.7
            }
        )
        db.add(azure_llm)
        logger.info("Universal Azure LLM seeded")

    db.commit()

def main() -> None:
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
