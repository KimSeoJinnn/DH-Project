# app/crud.py

from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext  # 👈 이 줄이 없으면 에러남!

# 암호화 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 1. 유저 조회 (아이디로 찾기)
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# 2. 회원가입 (비밀번호 암호화 저장)
def create_user(db: Session, user: schemas.UserCreate):
    # 비밀번호 암호화
    hashed_password = pwd_context.hash(user.password)
    
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password, # 암호화된 비밀번호 저장
        height=user.height,
        weight=user.weight
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 3. 비밀번호 검증 (로그인용)
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 4. 운동 데이터 넣기 (기존 코드 유지)
def create_exercise(db: Session, exercise: schemas.ExerciseCreate):
    db_exercise = models.Exercise(**exercise.dict())
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

# 5. 랜덤 퀘스트 뽑기 (기존 코드 유지)
def get_random_quests(db: Session, limit: int = 3):
    import random
    exercises = db.query(models.Exercise).all()
    if len(exercises) < limit:
        return exercises
    return random.sample(exercises, limit)

# 6. 퀘스트 완료 처리 & 레벨업 (기존 코드 유지)
def complete_quest(db: Session, quest_data: schemas.QuestComplete):
    user = db.query(models.User).filter(models.User.id == quest_data.user_id).first()
    if not user:
        return None

    log = models.WorkoutLog(
        user_id=user.id,
        quest_name=quest_data.quest_name,
        earned_xp=quest_data.earned_xp
    )
    db.add(log)

    user.xp += quest_data.earned_xp
    message = f"경험치 {quest_data.earned_xp} 획득! 👏"

    required_xp = user.level * 30
    if user.xp >= required_xp:
        user.level += 1
        user.xp -= required_xp
        message = f"🎉 축하합니다! Lv.{user.level} (으)로 성장했습니다!"
    
    db.commit()
    db.refresh(user)

    return {
        "message": message,
        "current_level": user.level,
        "current_xp": user.xp,
        "required_xp": user.level * 30
    }

# 7. 식단 기록 저장 (기존 코드 유지)
def create_meal_log(db: Session, user_id: int, traffic_light: str, feedback: str, xp: int):
    db_meal = models.MealLog(
        user_id=user_id,
        image_url="http://fake-image-url.com/food.jpg",
        traffic_light=traffic_light,
        feedback=feedback,
        earned_xp=xp
    )
    db.add(db_meal)
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.xp += xp
    
    db.commit()
    db.refresh(db_meal)
    return db_meal