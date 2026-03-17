import flet as ft
import requests
from datetime import datetime
import json
import os
import sys

SERVER_URL = "https://dh-fitness-app.onrender.com"
current_username = "" 

def main(page: ft.Page):
    global current_username
    current_level = 1
    current_title = "입문자" # 현재 칭호를 기억하는 변수
    
    page.title = "헬린이 키우기 (Developer Mode)"
    page.window.width = 400
    page.window.height = 700 
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "black"
    
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # -------------------------------------------------
    # 파일 경로 설정
    # -------------------------------------------------
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    DATA_FILE = os.path.join(script_dir, "quest_data.json")
    print(f"📂 데이터 저장 위치: {DATA_FILE}")

    # UI 컴포넌트 초기화
    level_text = ft.Text(value="Lv. 1 입문자", size=20, color="yellow", weight="bold")
    xp_text = ft.Text(size=12, color="white")
    xp_bar = ft.ProgressBar(width=300, color="orange", bgcolor="grey", value=0)
    
    quest_list_view = ft.Column(spacing=10, scroll="auto", height=280)

    # -------------------------------------------------
    # 메시지 함수
    # -------------------------------------------------
    def show_message(msg, color="green"):
        snack = ft.SnackBar(
            content=ft.Text(msg, color="white", weight="bold"),
            bgcolor=color,
            duration=2000
        )
        page.snack_bar = snack
        snack.open = True
        page.update()

    # -------------------------------------------------
    # [개발자용] 경험치 치트키 함수 (수정됨)
    # -------------------------------------------------
    def debug_add_xp(e, amount):
        nonlocal current_level, current_title
        
        # 1. API 요청 전, 현재 레벨을 '이전 레벨' 변수에 저장
        prev_level = current_level 

        if not current_username:
            show_message("로그인 먼저 하세요!", "red")
            return

        try:
            req_data = {
                "username": current_username, 
                "amount": amount,
                "exercise": "Debug Tool", 
                "count": "1"
            }
            res = requests.post(f"{SERVER_URL}/users/workout", json=req_data)
            
            if res.status_code == 200:
                result = res.json()
                new_level = result['new_level']
                current_xp = result['current_xp']
                new_title = result.get('title', '알 수 없음')
                
                # UI 갱신 (텍스트, 게이지)
                level_text.value = f"Lv.{new_level} {new_title}"
                xp_text.value = f"경험치: {current_xp} / 100 XP"
                xp_bar.value = current_xp / 100
                
                # 2. 레벨업 감지 로직 (퀘스트 완료 시와 동일한 팝업)
                if new_level > prev_level:
                    def close_levelup(e):
                        levelup_dlg.open = False
                        page.update()
                    
                    # 팝업 내용 구성
                    popup_content_controls = [
                        ft.Text(f"축하합니다! {current_username}님!", size=16),
                        ft.Text(f"Lv.{new_level} 달성!", size=16),
                    ]

                    # 칭호가 바뀌었을 때만 문구 추가
                    if new_title != current_title:
                        popup_content_controls.append(
                            ft.Text(f"이제 [{new_title}] 입니다!", size=18, color="green", weight="bold")
                        )
                    
                    popup_content_controls.append(
                        ft.Text(f"현재 경험치: {current_xp}/100", size=12, color="grey")
                    )

                    levelup_dlg = ft.AlertDialog(
                        title=ft.Text("🎉 레벨업!", size=20, color="amber"),
                        content=ft.Column(popup_content_controls, height=120, tight=True),
                        actions=[ft.FilledButton("확인", on_click=close_levelup)],
                    )
                    page.overlay.append(levelup_dlg)
                    levelup_dlg.open = True
                
                # 레벨업이 아닐 경우 그냥 토스트 메시지 띄우기
                else:
                    show_message(f"🧪 테스트: 경험치 {amount} 추가됨!", "blue")

                # 상태 업데이트
                current_level = new_level
                current_title = new_title
                
                page.update()
            else:
                show_message(f"에러: {res.status_code}", "red")
        except Exception as err:
            print(f"디버그 에러: {err}")
            show_message("연결 실패", "red")

    # -------------------------------------------------
    # 퀘스트 로드 & 클릭 이벤트
    # -------------------------------------------------
    def load_quests(e=None):
        quest_list_view.controls.clear()
        quest_list_view.controls.append(ft.Text("📜 오늘의 퀘스트", size=16, weight="bold"))
        
        today_date = datetime.now().strftime("%Y-%m-%d")
        current_quests = []
        all_data = {} 

        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    all_data = json.load(f)
            except: all_data = {}

        user_data = all_data.get(current_username, {})
        last_date = user_data.get("last_active_date")
        stored_quests = user_data.get("daily_quests")

        if last_date == today_date and stored_quests:
            print(f"💾 {current_username}님의 퀘스트 로드 (캐시)")
            current_quests = stored_quests
        else:
            print(f"🌐 {current_username}님의 새 퀘스트 요청 (서버)")
            try:
                res = requests.get(f"{SERVER_URL}/quests")
                if res.status_code == 200:
                    fetched_quests = res.json()
                    for q in fetched_quests: q['completed'] = False 
                    current_quests = fetched_quests
                    
                    all_data[current_username] = {
                        "last_active_date": today_date,
                        "daily_quests": current_quests
                    }
                    try:
                        with open(DATA_FILE, "w", encoding="utf-8") as f:
                            json.dump(all_data, f, ensure_ascii=False, indent=4)
                    except: pass
                else:
                    quest_list_view.controls.append(ft.Text("서버 에러", color="red"))
                    page.update()
                    return
            except:
                quest_list_view.controls.append(ft.Text("연결 실패", color="red"))
                page.update()
                return

        if len(current_quests) == 0:
            quest_list_view.controls.append(ft.Text("퀘스트가 없습니다.", color="grey"))
        else:
            for i, q in enumerate(current_quests):
                is_done = q.get('completed', False)
                icon_str = "✅" if is_done else "⬜"
                check_icon = ft.Text(icon_str, size=24)
                
                def on_card_click(e, index=i, quest_data=q, icon_widget=check_icon):
                    nonlocal current_level, current_title # 칭호 변수 가져오기
                    if icon_widget.value == "✅": return 

                    try:
                        req_data = {"username": current_username, "difficulty": quest_data['difficulty']}
                        prev_level = current_level

                        res = requests.post(f"{SERVER_URL}/quests/complete", json=req_data)

                        if res.status_code == 200:
                            result = res.json()
                            icon_widget.value = "✅"
                            
                            new_level = result['new_level']
                            current_xp = result['current_xp']
                            new_title = result.get('title', '알 수 없음') 

                            # UI 갱신
                            level_text.value = f"Lv.{new_level} {new_title}"
                            xp_text.value = f"경험치: {current_xp} / 100 XP"
                            xp_bar.value = current_xp / 100

                            # 레벨업 팝업 로직
                            if new_level > prev_level:
                                def close_levelup(e):
                                    levelup_dlg.open = False
                                    page.update()
                                
                                # 팝업 내용 구성
                                popup_content_controls = [
                                    ft.Text(f"축하합니다! {current_username}님!", size=16),
                                    ft.Text(f"Lv.{new_level} 달성!", size=16),
                                ]

                                # [수정] 칭호가 바뀌었을 때만 문구 추가
                                if new_title != current_title:
                                    popup_content_controls.append(
                                        ft.Text(f"이제 [{new_title}] 입니다!", size=18, color="green", weight="bold")
                                    )
                                
                                popup_content_controls.append(
                                    ft.Text(f"현재 경험치: {current_xp}/100", size=12, color="grey")
                                )

                                levelup_dlg = ft.AlertDialog(
                                    title=ft.Text("🎉 레벨업!", size=20, color="amber"),
                                    content=ft.Column(popup_content_controls, height=120, tight=True),
                                    actions=[ft.FilledButton("확인", on_click=close_levelup)],
                                )
                                page.overlay.append(levelup_dlg)
                                levelup_dlg.open = True
                            else:
                                show_message(f"💪 {result.get('message', '완료!')}", "green")

                            # 현재 상태 업데이트 (중요)
                            current_level = new_level
                            current_title = new_title 

                            # 파일 저장 로직
                            try:
                                if os.path.exists(DATA_FILE):
                                    with open(DATA_FILE, "r", encoding="utf-8") as f:
                                        current_all_data = json.load(f)
                                else: current_all_data = {}
                                
                                if current_username in current_all_data:
                                    current_all_data[current_username]['daily_quests'][index]['completed'] = True
                                    with open(DATA_FILE, "w", encoding="utf-8") as f:
                                        json.dump(current_all_data, f, ensure_ascii=False, indent=4)
                            except: pass
                            
                            page.update()
                        else: show_message(f"오류: {res.status_code}", "red")
                    except: show_message("연결 실패", "red")

                card = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(f"🔥 {q['name']}", size=16, weight="bold"),
                            ft.Text(f"목표: {q['count']} | 난이도: {q['difficulty']}", size=12, color="grey"),
                        ]),
                        check_icon 
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor="white10", padding=12, border_radius=10, width=300, on_click=on_card_click 
                )
                quest_list_view.controls.append(card)
        
        page.update()

    # -------------------------------------------------
    # 회원가입 팝업
    # -------------------------------------------------
    def show_signup_modal(e):
        new_id = ft.TextField(label="사용할 아이디", autofocus=True)
        new_pw = ft.TextField(label="사용할 비밀번호", password=True, can_reveal_password=True)
        signup_error_text = ft.Text("", color="red", size=12)

        def close_signup(e):
            signup_dlg.open = False
            page.update()

        def try_signup_enter(e):
            do_signup(e)

        def do_signup(e):
            signup_error_text.value = ""
            page.update()

            if not new_id.value or not new_pw.value:
                signup_error_text.value = "아이디와 비밀번호를 입력해주세요."
                page.update()
                return
            
            try:
                res = requests.post(f"{SERVER_URL}/users/signup", json={"username": new_id.value, "password": new_pw.value})
                if res.status_code == 200:
                    signup_dlg.open = False
                    username_input.value = new_id.value 
                    password_input.value = ""
                    login_error_text.value = "✅ 가입 성공! 로그인 해주세요."
                    login_error_text.color = "green"
                    page.update()
                elif res.status_code == 400:
                    try: msg = res.json().get('detail', '이미 존재하는 아이디입니다.')
                    except: msg = "이미 존재하는 아이디입니다."
                    signup_error_text.value = f"❌ {msg}"
                    page.update()
                else:
                    signup_error_text.value = "❌ 서버 오류"
                    page.update()
            except: 
                signup_error_text.value = "❌ 연결 실패"
                page.update()
        
        new_pw.on_submit = try_signup_enter

        signup_dlg = ft.AlertDialog(
            title=ft.Text("회원가입 👶"), 
            content=ft.Column([new_id, new_pw, signup_error_text], height=220, tight=True), 
            actions=[
                ft.TextButton("취소", on_click=close_signup),
                ft.FilledButton("가입하기", on_click=do_signup, style=ft.ButtonStyle(bgcolor="green", color="white"))
            ]
        )
        page.overlay.append(signup_dlg)
        signup_dlg.open = True
        page.update()

    # -------------------------------------------------
    # 랭킹 팝업
    # -------------------------------------------------
    def show_ranking(e):
        try:
            res = requests.get(f"{SERVER_URL}/users/ranking")
            if res.status_code == 200:
                rank_ui = []
                for i, u in enumerate(res.json()):
                    is_me = (u['username'] == current_username)
                    bg = "blue" if is_me else "white10"
                    rank_ui.append(ft.Container(content=ft.Row([ft.Text(f"{i+1}위 {u['username']}"), ft.Text(f"Lv.{u['level']}")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), padding=10, bgcolor=bg, border_radius=5))
                dlg = ft.AlertDialog(title=ft.Text("랭킹"), content=ft.Column(rank_ui, height=200, scroll="auto"), actions=[ft.TextButton("닫기", on_click=lambda e: setattr(dlg, 'open', False) or page.update())])
                page.overlay.append(dlg)
                dlg.open = True
                page.update()
        except: pass

    # -------------------------------------------------
    # [NEW] AI 식단 분석 팝업 (최신 Flet 버전 호환 ✨)
    # -------------------------------------------------
    def show_diet_modal(e):
        print("🚩 [START] 팝업창 열림") 

        def close_modal(e):
            diet_dlg.open = False
            page.update()

        # UI 요소
        food_input = ft.TextField(label="음식 이름 (예: 마라탕)", autofocus=True)
        result_text = ft.Text("음식을 입력하고 엔터를 누르세요.", size=14)
        
        # 🚦 1. 아이콘 대신 '진짜 빛나는 신호등' 만들기 (소문자 문자열로 변경!)
        traffic_light_ui = ft.Container(
            width=80, height=80, border_radius=40,
            bgcolor="grey300"
        )

        # -----------------------------------------------
        # 👇 여기가 핵심 분석 함수입니다
        # -----------------------------------------------
        def run_analysis(e):
            print("\n----------------------------------------")
            print("1️⃣ [클릭] 분석 버튼 눌림. 함수 시작.")
            
            if not food_input.value:
                print("⚠️ [경고] 음식 이름 없음.")
                return
            
            # 로딩 표시
            result_text.value = "⏳ AI 코치가 식단을 분석 중입니다..."
            traffic_light_ui.bgcolor = "grey300" # 👈 여기도 문자열!
            traffic_light_ui.shadow = None 
            page.update()
            
            try:
                target_url = f"http://127.0.0.1:8000/analyze?food={food_input.value}"
                res = requests.get(target_url, timeout=10)

                if res.status_code == 200:
                    data = res.json()

                    # 리스트 껍질 벗기기
                    if isinstance(data, list):
                        data = data[0] if len(data) > 0 else {}

                    # 키값 확인
                    if 'traffic_light' in data:
                        print("5️⃣ [성공] 필요한 데이터가 다 있습니다.")
                        
                        # 🚦 2. 신호등 색깔 맵핑 (에러 안 나게 문자열로 변경!)
                        color_map = {
                            "Green": "green500", 
                            "Yellow": "amber500", 
                            "Red": "red500"
                        }
                        
                        light_color = color_map.get(data['traffic_light'], "grey500")
                        traffic_light_ui.bgcolor = light_color
                        
                        # 🌟 핵심: 네온사인처럼 빛나는 그림자 효과 추가
                        traffic_light_ui.shadow = ft.BoxShadow(blur_radius=25, color=light_color)
                        
                        result_text.value = (
                            f"🍎 음식: {data.get('food_name', '음식')}\n"
                            f"🔥 칼로리: {data.get('calories')}kcal\n"
                            f"💪 단백질: {data.get('protein')}g\n\n"
                            f"💡 코치의 한마디:\n{data.get('reason')}"
                        )
                    else:
                        result_text.value = f"데이터 오류: {data}"
                else:
                    result_text.value = f"서버 에러 ({res.status_code})"

            except Exception as err:
                result_text.value = f"에러: {err}"
            
            page.update()
            print("----------------------------------------\n")

        food_input.on_submit = run_analysis

        # 팝업창 UI
        content_column = ft.Column(
            controls=[
                ft.Text("무엇을 드셨나요?", size=18, weight="bold"),
                ft.Container(height=10),
                food_input,
                ft.FilledButton("분석하기", on_click=run_analysis, bgcolor="blue", color="white"),
                ft.Divider(),
                ft.Row([traffic_light_ui], alignment="center"), 
                ft.Container(height=10),
                result_text
            ],
            width=300, scroll="auto", spacing=10 
        )

        diet_dlg = ft.AlertDialog(
            title=ft.Text("🥦 AI 식단 신호등"),
            content=content_column,
            actions=[ft.TextButton("닫기", on_click=close_modal)],
            actions_alignment="end"
        )
        
        page.overlay.append(diet_dlg)
        diet_dlg.open = True
        page.update()

    # -------------------------------------------------
    # 로그인 함수
    # -------------------------------------------------
    login_error_text = ft.Text("", color="red")  
    
    def login_click(e):
        global current_username
        nonlocal current_level, current_title
        
        login_error_text.value = ""
        page.update()

        if not username_input.value or not password_input.value: return
        
        try:
            res = requests.post(f"{SERVER_URL}/users/login", json={"username": username_input.value, "password": password_input.value})
            if res.status_code == 200:
                data = res.json()
                current_username = data['username']
                current_level = data['level']
                user_title = data.get('title', '초보자')
                
                # [수정] 로그인 시 현재 칭호 저장
                current_title = user_title

                level_text.value = f"Lv.{current_level} {user_title}"
                xp_text.value = f"경험치: {data.get('exp', 0)} / 100 XP"
                xp_bar.value = data.get('exp', 0) / 100
                xp_bar.width = 300

                page.clean()
                page.vertical_alignment = ft.MainAxisAlignment.START 
                
                page.add(ft.Column([
                    ft.Container(height=20),
                    ft.Text(f"🔥 {current_username} 님!", size=25, weight="bold"),
                    ft.Container(height=20),
                    level_text, 
                    ft.Container(height=10),
                    xp_bar, xp_text,
                    
                    ft.Container(height=10),
                    ft.Row([
                        ft.FilledButton("🧪 +25 XP", on_click=lambda e: debug_add_xp(e, 25), style=ft.ButtonStyle(bgcolor="grey")),
                        ft.FilledButton("🧪 +95 XP", on_click=lambda e: debug_add_xp(e, 95), style=ft.ButtonStyle(bgcolor="red")),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    
                    ft.Container(height=20),
                    quest_list_view,
                    ft.Container(height=10),

                    ft.FilledButton(
                        "🥦 식단 분석하기", 
                        width=300, 
                        height=50, 
                        style=ft.ButtonStyle(bgcolor="orange", color="white"), 
                        on_click=show_diet_modal
                    ),
                    ft.Container(height=10),

                    ft.FilledButton("랭킹 보기 🏆", width=300, height=50, style=ft.ButtonStyle(bgcolor="green", color="white"), on_click=show_ranking)
                ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
                
                page.update()
                load_quests()
            elif res.status_code == 400:
                try: error_msg = res.json().get('detail', '로그인 실패')
                except: error_msg = "아이디/비밀번호 확인"
                login_error_text.value = f"⚠️ {error_msg}"
                page.update()
            else:
                login_error_text.value = "❌ 서버 오류"
                page.update()
        except Exception as err:
            login_error_text.value = f"연결 에러: {err}"
            page.update()

    # -------------------------------------------------
    # 초기 화면
    # -------------------------------------------------
    username_input = ft.TextField(label="아이디", width=300, autofocus=True)
    password_input = ft.TextField(label="비밀번호", width=300, password=True, can_reveal_password=True, on_submit=login_click)
    
    login_btn = ft.FilledButton("로그인", width=300, height=50, on_click=login_click)
    signup_btn = ft.TextButton("회원가입", on_click=show_signup_modal)
    
    page.add(ft.Column([
        ft.Container(height=50), 
        ft.Text("🏋️", size=70),
        ft.Container(height=20),
        username_input, password_input, 
        ft.Container(height=10),
        login_error_text,
        login_btn, 
        signup_btn
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER))

ft.run(main)