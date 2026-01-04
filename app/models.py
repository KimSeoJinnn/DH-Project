from sqlalchemy import Boolean, Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)

# ★ [추가됨] 운동 퀘스트 종류를 저장할 테이블
class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)       # 운동 이름 (예: 스쿼트)
    count = Column(String)      # 목표 횟수 (예: 20회)
    difficulty = Column(String) # 난이도 (예: 상/중/하)