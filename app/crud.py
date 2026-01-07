from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from datetime import datetime, timedelta
import random

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ [중요] 칭호 함수를 가장 먼저 정의합니다. (에러 방지)
def get_user_title(level: int):
    if level <= 5:
        return "🦴 흔들리는 갈대 (초보)"
    elif level <= 10:
        return "🐥 헬스장 병아리 (입문)"
    elif level <= 20:
        return "🏃‍♂️ 성실한 헬린이 (중수)"
    elif level <= 30:
        return "💪 근육이 꿈틀꿈틀 (고수)"
    elif level <= 50:
        return "🏋️‍♂️ 헬스장 고인물 (초고수)"
    else:
        return "👑 근육의 신 (마스터)"

# -------------------------------------------------
# 유저 관련 함수 (회원가입, 로그인, 비밀번호 검증)
# -------------------------------------------------
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    # 초기 생성 시 레벨 1, 경험치 0
    db_user = models.User(username=user.username, hashed_password=hashed_password, level=1, exp=0)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# -------------------------------------------------
# 퀘스트(루틴) 관련 함수 - 요일별 자동 생성
# -------------------------------------------------
def get_today_routine():
    # 1. 서버 시간(UTC)을 한국 시간(KST)으로 변환
    utc_now = datetime.utcnow()
    kst_now = utc_now + timedelta(hours=9)
    weekday = kst_now.weekday() # 0:월, 1:화, ... 5:토, 6:일
    
    # 디버깅용 로그 (Render 로그에서 확인 가능)
    print(f"Current KST: {kst_now}, Weekday: {weekday}")

    # 기본: 휴식 루틴 (월, 수, 금, 일)
    exercises = [
        {"name": "가벼운 스트레칭", "count": "10분", "difficulty": "하"},
        {"name": "물 마시기", "count": "1리터", "difficulty": "하"},
        {"name": "충분한 수면", "count": "7시간", "difficulty": "하"}
    ]

    # 화요일(1), 목요일(3) - 전신 루틴
    if weekday in [1, 3]:
        exercises = [
            {"name": "스쿼트", "count": "15회 x 3세트", "difficulty": "중"},
            {"name": "푸쉬업", "count": "12회 x 3세트", "difficulty": "중"},
            {"name": "렛풀다운", "count": "12회 x 3세트", "difficulty": "중"},
            {"name": "플랭크", "count": "40초 x 2세트", "difficulty": "중"}
        ]
    
    # 토요일(5) - 불토 고강도 하체
    elif weekday == 5:
        exercises = [
            {"name": "스쿼트", "count": "20회 x 4세트", "difficulty": "상"},
            {"name": "런지", "count": "15회(양발)", "difficulty": "상"},
            {"name": "버피테스트", "count": "15회", "difficulty": "상"},
            {"name": "레그레이즈", "count": "20회", "difficulty": "중"}
        ]

    return exercises

# -------------------------------------------------
# 퀘스트 완료 처리 함수
# -------------------------------------------------
def complete_quest(db: Session, request: schemas.QuestComplete):
    user = get_user_by_username(db, request.username)
    if not user: return None
    
    # 난이도별 경험치 설정
    xp_map = {"하": 5, "중": 10, "상": 15, "최상": 20}
    gain_xp = xp_map.get(request.difficulty, 5)

    user.exp += gain_xp
    message = f"보상 획득! (+{gain_xp} XP)"

    # 레벨업 로직 (경험치 100 차면 레벨업)
    if user.exp >= 100:
        user.level += 1
        user.exp -= 100 
        message = f"🎉 레벨업! (Lv.{user.level})"

    db.commit()
    db.refresh(user)

    # ✅ 리턴값에 'title'을 꼭 포함해야 클라이언트가 표시할 수 있음
    return {
        "message": message, 
        "new_level": user.level, 
        "current_xp": user.exp, 
        "gained_xp": gain_xp,
        "title": get_user_title(user.level) 
    }