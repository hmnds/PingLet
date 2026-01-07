from sqlalchemy import create_engine, text

creds = [
    "postgresql://pinglet:pinglet@localhost:5432/pinglet",
    "postgresql://postgres:postgres@localhost:5432/pinglet",
    "postgresql://postgres:password@localhost:5432/pinglet",
    "postgresql://postgres:@localhost:5432/pinglet",
    "postgresql://hasithwireapps:@localhost:5432/pinglet",
    "postgresql://hasithwireapps:@localhost:5432/postgres",
]

for url in creds:
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            print(f"SUCCESS: {url}")
            # Try to create simple table
            try:
                conn.execute(text("CREATE TABLE IF NOT EXISTS test_perm (id serial primary key)"))
                conn.execute(text("DROP TABLE test_perm"))
                print("  -> Can create tables!")
            except Exception as e:
                print(f"  -> Cannot create tables: {e}")
    except Exception as e:
        print(f"FAIL: {url} - {e}")
