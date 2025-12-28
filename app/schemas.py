# app/schemas.py

from pydantic import BaseModel
from typing import Optional, Union  # "값이 없을 수도 있음(None)"을 표현하기 위해 가져옴
from datetime import date           # 날짜 처리를 위해 가져옴

# ==========================================
# 1. 회원(User) 관련 스키마
# ==========================================

# [회원가입] 사용자가 가입할 때 보낼 정보
class UserCreate(BaseModel):
    username: str
    password: str   # "1234" 같은 비밀번호 (서버가 받아서 암호화함)
    height: int
    weight: int

# [로그인] 사용자가 로그인할 때 보낼 정보
# ★ 중요: 이게 없으면 로그인 기능을 못 만듭니다!
class UserLogin(BaseModel):
    username: str
    password: str

# [응답] 내 정보 보기 등을 할 때 서버가 돌려줄 정보
# 비밀번호는 보안상 절대 돌려주면 안 되므로 뺐습니다.
class UserResponse(BaseModel):
    id: int
    username: str
    level: int
    xp: int
    
    # DB 데이터를 Pydantic 모델로 변환할 때 필요함 (필수 설정)
    class Config:
        from_attributes = True


# ==========================================
# 2. 운동(Exercise) 관련 스키마
# ==========================================

# [생성] 운동 데이터를 처음 만들 때 필요한 정보
class ExerciseCreate(BaseModel):
    name: str           # 운동 이름 (예: 스쿼트)
    category: str       # 부위 (예: 하체, 전신)
    description: Optional[str] = None  # 설명 (없어도 됨)
    xp_value: int = 10  # 이거 하면 주는 경험치

# [조회] 운동 목록을 보여줄 때 쓰는 틀
class ExerciseResponse(BaseModel):
    id: int
    name: str
    category: str
    description: Union[str, None] = None # 설명은 없을 수도 있음 (None 허용)
    xp_value: int

    class Config:
        from_attributes = True


# ==========================================
# 3. 퀘스트(Quest) 관련 스키마
# ==========================================

# [요청] 사용자가 "나 퀘스트 깼어요!" 하고 보낼 데이터
class QuestComplete(BaseModel):
    user_id: int        # 누가 깼는지
    quest_name: str     # 무슨 운동을 했는지
    earned_xp: int      # 경험치 얼마 받았는지

# [응답] 퀘스트 완료 후 서버가 "축하합니다!" 하고 보낼 데이터
class QuestResponse(BaseModel):
    message: str        # "경험치 10 획득!" 또는 "레벨업 성공!"
    current_level: int  # 현재 레벨
    current_xp: int     # 현재 경험치
    required_xp: int    # 다음 레벨까지 남은 경험치


# ==========================================
# 4. 식단(Meal) 관련 스키마
# ==========================================

# [응답] AI가 분석한 식단 결과를 프론트엔드에 줄 때
class MealResponse(BaseModel):
    traffic_light: str  # "🟢", "🟡", "🔴" 신호등 결과
    feedback: str       # "단백질이 부족해요" 같은 피드백
    earned_xp: int      # 획득한 경험치
    image_url: Optional[str] = None # 음식 사진 주소 (없을 수도 있음)

    class Config:
        from_attributes = True