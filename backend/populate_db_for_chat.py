import sys
import structlog
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import MonitoredAccount
from app.services.ingestion import IngestionService
from app.services.x_client import MockXClient
from app.services.embeddings import EmbeddingsService

# Configure logging
structlog.configure(
    processors=[structlog.dev.ConsoleRenderer()],
)
logger = structlog.get_logger()

def populate():
    db = SessionLocal()
    try:
        # 1. Ensure we have an account
        account = db.query(MonitoredAccount).filter(MonitoredAccount.username == "elonmusk").first()
        if not account:
            print("Creating mock account for @elonmusk...")
            account = MonitoredAccount(
                username="elonmusk",
                x_user_id="mock_12345",
                digest_enabled=True,
                alerts_enabled=True
            )
            db.add(account)
            db.commit()
            db.refresh(account)
        else:
            print("Found existing account @elonmusk")

        # 2. Run ingestion with embedding generation
        print("Running ingestion with embedding generation...")
        x_client = MockXClient()
        embeddings_service = EmbeddingsService()
        
        if not embeddings_service.client:
            print("❌ WARNING: OpenAI API Key is missing! Embeddings will be zero-vectors and Chat will NOT work.")
        else:
            print("✅ OpenAI API Key found.")

        service = IngestionService(x_client, db, embeddings_service)
        result = service.ingest_account(account.id)
        
        print(f"Ingestion result: {result}")
        print("✅ Database populated with posts and embeddings!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate()
