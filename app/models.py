from sqlalchemy import Boolean, Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)

# ★ [중요] 이 부분이 빠져있거나 오타가 있으면 500 에러가 납니다!
class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)       # 운동 이름
    count = Column(String)      # 목표 횟수
    difficulty = Column(String) # 난이도