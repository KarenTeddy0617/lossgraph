from sqlalchemy import text

from app.db.session import engine


def main():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection successful!")
            print("Result:", result.scalar())

    except Exception as e:
        print("Database connection failed.")
        print(type(e).__name__)
        print(e)


if __name__ == "__main__":
    main()