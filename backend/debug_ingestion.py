import structlog
from app.database import SessionLocal
from app.services.ingestion import IngestionService
from app.services.x_client import RealXClient
from app.config import settings

# Configure logging to see output
structlog.configure(
    processors=[structlog.dev.ConsoleRenderer()],
)
logger = structlog.get_logger()

def debug_ingestion():
    print("="*50)
    print("DEBUG INGESTION")
    print("="*50)
    
    # 1. Check Token
    token = settings.x_api_bearer_token
    if not token or token == "your_x_api_bearer_token_here":
        print("❌ Token is missing or default in settings!")
        return
    print(f"✅ Token found (len={len(token)})")

    # 2. Setup Service
    db = SessionLocal()
    try:
        client = RealXClient()
        service = IngestionService(client, db)
        
        print("\n--- Starting Ingest All Accounts ---")
        result = service.ingest_all_accounts()
        print("\n--- Result ---")
        print(result)
        
        print("\nerrors encountered:")
        for err in result.get("errors", []):
            print(f" - {err}")
            
    except Exception as e:
        print(f"❌ Exception during ingestion: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_ingestion()
