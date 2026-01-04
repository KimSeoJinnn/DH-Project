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
    db_user = models.User(username=user.username, hashed_password=hashed_password, level=1, exp=0)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# --- 퀘스트 관련 ---
def initialize_exercises(db: Session):
    if db.query(models.Exercise).first(): return None
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

def get_random_quests(db: Session, limit: int = 3):
    exercises = db.query(models.Exercise).all()
    if not exercises:
        initialize_exercises(db)
        exercises = db.query(models.Exercise).all()
    if len(exercises) < limit: return exercises
    return random.sample(exercises, limit)

# ★ [확인] request.difficulty를 쓰는지 확인하세요!
def complete_quest(db: Session, request: schemas.QuestComplete):
    user = get_user_by_username(db, request.username)
    if not user: return None
    
    xp_map = {"하": 5, "중": 10, "상": 15, "최상": 20}
    gain_xp = xp_map.get(request.difficulty, 5)

    user.exp += gain_xp
    message = f"보상 획득! (+{gain_xp} XP)"

    if user.exp >= 100:
        user.level += 1
        user.exp -= 100 
        message = f"🎉 레벨업! (Lv.{user.level})"

    db.commit()
    db.refresh(user)

    return {"message": message, "new_level": user.level, "current_xp": user.exp, "gained_xp": gain_xp}