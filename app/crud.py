# app/crud.py
from sqlalchemy.orm import Session
from app import models, schemas

# 1. 아이디 중복 확인
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# 2. 사용자 생성 (암호화 없이 저장!)
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        password=user.password,  # "1234"가 그대로 DB에 저장됨
        height=user.height,
        weight=user.weight
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# 3. 운동 데이터가 하나도 없으면 기초 데이터 5개 넣기
def initialize_exercises(db: Session):
    # 이미 데이터가 있는지 확인 (있으면 스킵)
    if db.query(models.Exercise).first():
        return None
    
    # 기초 데이터 리스트
    exercises = [
        models.Exercise(name="푸시업", part="가슴", difficulty="하", tip="허리가 꺾이지 않게 주의!", video_url="youtube.com/pushup"),
        models.Exercise(name="스쿼트", part="하체", difficulty="중", tip="무릎이 발끝을 넘지 않게!", video_url="youtube.com/squat"),
        models.Exercise(name="런지", part="하체", difficulty="중", tip="상체를 곧게 세우세요.", video_url="youtube.com/lunge"),
        models.Exercise(name="플랭크", part="코어", difficulty="하", tip="엉덩이를 너무 들지 마세요.", video_url="youtube.com/plank"),
        models.Exercise(name="벤치프레스", part="가슴", difficulty="상", tip="손목이 꺾이지 않게 주의!", video_url="youtube.com/bench")
    ]
    
    db.add_all(exercises)
    db.commit()
    return "기초 운동 데이터 생성 완료! 💪"

# 4. 랜덤으로 운동 3개 뽑아오기 (오늘의 퀘스트)
from sqlalchemy.sql import func

def get_random_quests(db: Session, limit: int = 3):
    # 랜덤 정렬(func.random)해서 3개 가져오기
    return db.query(models.Exercise).order_by(func.random()).limit(limit).all()




# 5. 퀘스트 완료 처리 & 레벨업 시스템
def complete_quest(db: Session, quest_data: schemas.QuestComplete):
    # 1. 사용자 찾기
    user = db.query(models.User).filter(models.User.id == quest_data.user_id).first()
    if not user:
        return None # 유저가 없으면 종료

    # 2. 기록장에 기록 남기기 (Log)
    log = models.WorkoutLog(
        user_id=user.id,
        quest_name=quest_data.quest_name,
        earned_xp=quest_data.earned_xp
    )
    db.add(log)

    # 3. 경험치 지급
    user.xp += quest_data.earned_xp
    message = f"경험치 {quest_data.earned_xp} 획득! 👏"

    # 4. 레벨업 판단 로직 (단순화: 필요 경험치 = 레벨 * 30)
    required_xp = user.level * 30

    # 경험치가 통을 넘쳤다면? -> 레벨업!
    if user.xp >= required_xp:
        user.level += 1             # 레벨 1 증가
        user.xp -= required_xp      # 경험치 통 비우기 (남은 건 이월)
        message = f"🎉 축하합니다! Lv.{user.level} (으)로 성장했습니다!"
    
    # 5. DB 저장
    db.commit()
    db.refresh(user)

    # 6. 결과 반환
    return {
        "message": message,
        "current_level": user.level,
        "current_xp": user.xp,
        "required_xp": user.level * 30
    }



# 6. 식단 기록 저장 & 경험치 지급
def create_meal_log(db: Session, user_id: int, traffic_light: str, feedback: str, xp: int):
    # 1. 기록 저장
    db_meal = models.MealLog(
        user_id=user_id,
        image_url="http://fake-image-url.com/food.jpg", # 이미지는 일단 가짜 주소로 저장
        traffic_light=traffic_light,
        feedback=feedback,
        earned_xp=xp
    )
    db.add(db_meal)
    
    # 2. 사용자에게 경험치 지급
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.xp += xp
        # (여기서도 레벨업 로직을 넣을 수 있지만, 코드가 길어지니 생략합니다)
    
    db.commit()
    db.refresh(db_meal)
    return db_meal