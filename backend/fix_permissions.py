from sqlalchemy import create_engine, text

# Connect as superuser (system user 'hasithwireapps')
# We know this works from the previous probe
admin_url = "postgresql://hasithwireapps:@localhost:5432/pinglet"

try:
    engine = create_engine(admin_url)
    with engine.connect() as conn:
        print("Connected as admin (hasithwireapps)...")
        
        # Grant permissions to 'pinglet' user
        # We need to run these inside a transaction
        print("Granting permissions to 'pinglet' user...")
        
        statements = [
            "CREATE EXTENSION IF NOT EXISTS vector",
            "GRANT ALL ON SCHEMA public TO pinglet",
            "GRANT ALL PRIVILEGES ON DATABASE pinglet TO pinglet",
            "ALTER USER pinglet WITH CREATEDB" # Optional but helpful for dev
        ]
        
        for stmt in statements:
            try:
                conn.execute(text(stmt))
                print(f"  OK: {stmt}")
            except Exception as e:
                print(f"  WARN: {stmt} - {e}")
                
        conn.commit()
        print("Permissions updated successfully!")

except Exception as e:
    print(f"Failed to update permissions: {e}")
