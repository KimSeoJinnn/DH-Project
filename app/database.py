from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base # ★ 이 줄이 필요합니다
from sqlalchemy.orm import sessionmaker

# 현재 폴더에 sql_app.db 라는 파일을 만들어서 저장하겠다는 뜻
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app_V2_.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ★ [중요] 이 줄이 없어서 에러가 났던 겁니다!
Base = declarative_base()