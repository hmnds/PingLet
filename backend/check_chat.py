from app.config import settings
from app.database import SessionLocal
from app.models import Post
from sqlalchemy import func

def check_chat_health():
    print("="*60)
    print("Chat Feature Diagnostic")
    print("="*60)
    
    # 1. Check OpenAI Key
    key = settings.openai_api_key
    if not key:
        print("❌ OPENAI_API_KEY is NOT set.")
        print("   Chat requires an OpenAI API key to generate embeddings and answers.")
    else:
        print(f"✅ OPENAI_API_KEY is set (length: {len(key)})")
        
    # 2. Check Posts and Embeddings
    db = SessionLocal()
    try:
        total_posts = db.query(func.count(Post.id)).scalar()
        posts_with_embeddings = db.query(func.count(Post.id)).filter(Post.embedding.isnot(None)).scalar()
        
        print(f"\nTotal Posts in DB: {total_posts}")
        print(f"Posts with Embeddings: {posts_with_embeddings}")
        
        if total_posts > 0 and posts_with_embeddings == 0:
            print("\n⚠️  Issue: Posts exist but have NO embeddings.")
            print("   RAG Search will fail. This usually happens if:")
            print("   1. OpenAI key was missing during ingestion")
            print("   2. Ingestion service doesn't auto-generate embeddings (it's currently extracting them lazily in AlertEngine)")
            
    finally:
        db.close()
        
    print("\nRecommendation:")
    if not key:
        print("- Add OPENAI_API_KEY to backend/.env")
    print("- Ensure embeddings are generated upon ingestion")

if __name__ == "__main__":
    check_chat_health()
