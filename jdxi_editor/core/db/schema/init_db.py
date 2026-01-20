# init_db.py (or wherever you set up your DB)
from pathlib import Path
from sqlalchemy import create_engine
from models import Base

def init_db(db_url: str):
    engine = create_engine(db_url, future=True)
    # This will create all tables that do not yet exist
    Base.metadata.create_all(engine)

    # If you need to return a Session for ORM operations:
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine, future=True)
    return Session

# Example usage
if __name__ == "__main__":
    # SQLite example (no raw SQL)
    db_path = Path("data/mydb.sqlite3")
    init_db(f"sqlite+pysqlite:///{db_path.as_posix()}")
