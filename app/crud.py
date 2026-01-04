from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
import random

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 유저 관련 ---
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username, 
        hashed_password=hashed_password,
        level=1,
        exp=0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# --- ★ [추가됨] 퀘스트(운동) 관련 기능 ---

# 1. 운동 데이터가 없으면 자동으로 5개 채워넣기 (초기화)
def initialize_exercises(db: Session):
    # 이미 데이터가 있으면 패스
    if db.query(models.Exercise).first():
        return None
    
    # 기본 운동 리스트
    sample_exercises = [
        models.Exercise(name="스쿼트", count="15회", difficulty="하"),
        models.Exercise(name="스쿼트", count="30회", difficulty="중"),
        models.Exercise(name="스쿼트", count="45회", difficulty="상"),
        models.Exercise(name="싯업", count="15회", difficulty="하"),
        models.Exercise(name="싯업", count="30회", difficulty="중"),
        models.Exercise(name="싯업", count="45회", difficulty="상"),
        models.Exercise(name="푸쉬업", count="5회", difficulty="하"),
        models.Exercise(name="푸쉬업", count="15회", difficulty="중"),
        models.Exercise(name="푸쉬업", count="30회", difficulty="상"),
        models.Exercise(name="푸쉬업", count="45회", difficulty="최상"),
        models.Exercise(name="플랭크", count="30초", difficulty="중"),
        models.Exercise(name="플랭크", count="1분", difficulty="상"),
        models.Exercise(name="런지", count="15회(양발)", difficulty="상"),
        models.Exercise(name="런지", count="30회(양발)", difficulty="최상"),
        models.Exercise(name="버피테스트", count="10회", difficulty="상"),
        models.Exercise(name="버피테스트", count="20회", difficulty="최상"),
    ]
    
    db.add_all(sample_exercises)
    db.commit()
    return "운동 데이터 생성 완료!"

# 2. 랜덤으로 퀘스트 3개 뽑아주기
def get_random_quests(db: Session, limit: int = 3):
    exercises = db.query(models.Exercise).all()
    # 데이터가 3개보다 적으면 있는 거 다 주고, 많으면 랜덤 3개 뽑기
    if len(exercises) < limit:
        return exercises
    return random.sample(exercises, limit)