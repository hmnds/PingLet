from app.database import SessionLocal
from app.models import MonitoredAccount, Post

def inspect_db():
    db = SessionLocal()
    try:
        print("--- Monitored Accounts ---")
        accounts = db.query(MonitoredAccount).all()
        for acc in accounts:
            print(f"ID: {acc.id}, Username: {acc.username}, X_User_ID: {acc.x_user_id}")
            
        print("\n--- Recent Posts ---")
        posts = db.query(Post).order_by(Post.created_at.desc()).limit(5).all()
        for post in posts:
            print(f"Account: {post.author_id}, Text: {post.text[:50]}...")
            
    finally:
        db.close()

if __name__ == "__main__":
    inspect_db()
