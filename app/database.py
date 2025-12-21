# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 현재 폴더에 sql_app.db 라는 파일을 만들어서 저장하겠다는 뜻
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)