from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

USER = "administrador"
PASSWORD = "kali"
HOST = "localhost"
DB = "victor_gonzalez"

DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
