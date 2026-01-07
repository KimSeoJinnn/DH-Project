from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from datetime import datetime, timedelta
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
# def initialize_exercises(db: Session):
#     if db.query(models.Exercise).first(): return None
#     sample_exercises = [
#         models.Exercise(name="스쿼트", count="15회", difficulty="하"),
#         models.Exercise(name="스쿼트", count="30회", difficulty="중"),
#         models.Exercise(name="스쿼트", count="45회", difficulty="상"),
#         models.Exercise(name="싯업", count="15회", difficulty="하"),
#         models.Exercise(name="싯업", count="30회", difficulty="중"),
#         models.Exercise(name="싯업", count="45회", difficulty="상"),
#         models.Exercise(name="푸쉬업", count="5회", difficulty="하"),
#         models.Exercise(name="푸쉬업", count="15회", difficulty="중"),
#         models.Exercise(name="푸쉬업", count="30회", difficulty="상"),
#         models.Exercise(name="푸쉬업", count="45회", difficulty="최상"),
#         models.Exercise(name="플랭크", count="30초", difficulty="중"),
#         models.Exercise(name="플랭크", count="1분", difficulty="상"),
#         models.Exercise(name="런지", count="15회(양발)", difficulty="상"),
#         models.Exercise(name="런지", count="30회(양발)", difficulty="최상"),
#         models.Exercise(name="버피테스트", count="10회", difficulty="상"),
#         models.Exercise(name="버피테스트", count="20회", difficulty="최상"),
#     ]
#     db.add_all(sample_exercises)
#     db.commit()
#     return "운동 데이터 생성 완료!"

# [NEW] 요일별 고정 루틴 반환 함수
def get_today_routine():
    # 👈 [2] 서버 시간(UTC)에 9시간을 더해 한국 시간으로 변환
    utc_now = datetime.utcnow()
    kst_now = utc_now + timedelta(hours=9)
    
    # 한국 시간 기준으로 요일 확인 (0:월 ~ 6:일)
    weekday = kst_now.weekday()
    
    # 디버깅용 로그 (서버 로그에서 확인 가능)
    print(f"Current KST Time: {kst_now}, Weekday: {weekday}")

    # 기본 휴식 루틴 (월, 수, 금, 일)
    routine_type = "휴식 & 스트레칭 🧘"
    exercises = [
        {"name": "가벼운 스트레칭", "count": "10분", "difficulty": "하"},
        {"name": "물 마시기", "count": "1리터", "difficulty": "하"},
        {"name": "충분한 수면", "count": "7시간", "difficulty": "하"}
    ]

    # 화요일 (1), 목요일 (3) - 무분할 전신
    if weekday in [1, 3]:
        routine_type = "무분할 전신 💪"
        exercises = [
            {"name": "스쿼트", "count": "15회 x 3세트", "difficulty": "중"},
            {"name": "푸쉬업", "count": "12회 x 3세트", "difficulty": "중"},
            {"name": "렛풀다운(또는 턱걸이)", "count": "12회 x 3세트", "difficulty": "중"},
            {"name": "플랭크", "count": "40초 x 2세트", "difficulty": "중"}
        ]
    
    # 토요일 (5) - 불타는 고강도
    elif weekday == 5:
        routine_type = "🔥 불토 고강도 하체"
        exercises = [
            {"name": "스쿼트", "count": "20회 x 4세트", "difficulty": "상"},
            {"name": "런지", "count": "15회(양발) x 3세트", "difficulty": "상"},
            {"name": "버피테스트", "count": "15회 x 3세트", "difficulty": "상"},
            {"name": "레그레이즈", "count": "20회 x 3세트", "difficulty": "중"}
        ]

    return exercises

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