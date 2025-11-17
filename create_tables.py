from database import engine, Base
from models import User, AuthToken

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        print(f"✅ Created table: user_tbl")
        print(f"✅ Created table: auth_token")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()
