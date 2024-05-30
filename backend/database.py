from sqlmodel import SQLModel, create_engine, Session, select

sql_file_name = "database.db"
sqlite_url = f"sqlite:///{sql_file_name}"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
