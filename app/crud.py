from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
import random # 랜덤 뽑기용

# 암호화 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 1. 유저 조회
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# 2. 회원가입
def create_user(db: Session, user: schemas.UserCreate):
    # 비밀번호 암호화
    hashed_password = pwd_context.hash(user.password)
    
    # ★ [수정] height, weight 제거 (스키마랑 맞춤)
    # ★ [수정] exp=0 명시적 추가
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

# 3. 비밀번호 검증
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# ★ [복구] 이게 없어서 main.py에서 에러가 날 뻔했습니다!
def initialize_exercises(db: Session):
    # 이미 데이터가 있으면 패스
    if db.query(models.Exercise).first():
        return None
    
    # 기초 데이터 생성
    exercises = [
        models.Exercise(name="스쿼트", category="하체", description="허벅지와 엉덩이 근육 강화"),
        models.Exercise(name="푸시업", category="상체", description="가슴과 팔 근육 강화"),
        models.Exercise(name="플랭크", category="전신", description="코어 근육 강화"),
        models.Exercise(name="런지", category="하체", description="다리 근력 및 균형 감각 향상"),
        models.Exercise(name="버피 테스트", category="전신", description="유산소 및 전신 근력 운동")
    ]
    
    db.add_all(exercises)
    db.commit()
    return "기초 운동 데이터 생성 완료!"

# 4. 랜덤 퀘스트 뽑기
def get_random_quests(db: Session, limit: int = 3):
    exercises = db.query(models.Exercise).all()
    if not exercises: # 데이터가 없으면 빈 리스트 반환
        return []
        
    if len(exercises) < limit:
        return exercises
    return random.sample(exercises, limit)

# 5. 퀘스트 완료 처리
def complete_quest(db: Session, quest_data: schemas.QuestComplete):
    user = db.query(models.User).filter(models.User.username == quest_data.username).first()
    if not user:
        return None

    # ★ [수정] xp -> exp 로 변경
    user.exp += 10 # 퀘스트 완료 시 경험치 10
    
    # 레벨업 로직
    if user.exp >= 100:
        user.level += 1
        user.exp = 0
    
    db.commit()
    db.refresh(user)

    # 스키마(QuestResponse) 형태에 맞춰 반환하려면 조금 복잡하니
    # 여기서는 간단히 유저 정보만 업데이트하고 끝냅니다.
    # 실제 응답은 main.py에서 처리하는 게 보통입니다.
    return user

# 6. 식단 기록 저장
def create_meal_log(db: Session, user_id: int, traffic_light: str, feedback: str, xp: int):
    db_meal = models.MealLog(
        user_id=user_id,
        image_url="http://fake-image-url.com/food.jpg", # 임시 이미지
        traffic_light=traffic_light,
        feedback=feedback,
        earned_xp=xp
    )
    db.add(db_meal)
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        # ★ [수정] xp -> exp 로 변경
        user.exp += xp
        # 식단에서도 레벨업 체크
        if user.exp >= 100:
            user.level += 1
            user.exp = 0
    
    db.commit()
    db.refresh(db_meal)
    return db_meal
