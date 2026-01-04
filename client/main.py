import flet as ft
import requests
from datetime import datetime
import json
import os

SERVER_URL = "https://dh-fitness-app.onrender.com"
current_username = "" 

def main(page: ft.Page):
    global current_username
    current_level = 1
    
    page.title = "헬린이 키우기"
    page.window.width = 400
    page.window.height = 700 
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "black"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    level_text = ft.Text(size=24, color="yellow", weight="bold")
    xp_text = ft.Text(size=12, color="white")
    xp_bar = ft.ProgressBar(width=200, color="orange", bgcolor="grey", value=0)
    
    quest_list_view = ft.Column(spacing=10, scroll="auto", height=280)

    # -------------------------------------------------
    # 🔔 [수정] 메시지 띄우기 (모든 버전 호환)
    # -------------------------------------------------
    def show_message(msg, color="green"):
        # 1. 스낵바 생성
        snack = ft.SnackBar(
            content=ft.Text(msg, color="white", weight="bold"),
            bgcolor=color,
            duration=2000
        )
        # 2. 페이지 속성에 할당하고 open=True 설정
        page.snack_bar = snack
        snack.open = True
        page.update()

    # -------------------------------------------------
    # 📜 퀘스트 불러오기 (팝업창 오류 수정됨)
    # -------------------------------------------------
    def load_quests(e=None):
        quest_list_view.controls.clear()
        quest_list_view.controls.append(ft.Text("📜 오늘의 퀘스트", size=16, weight="bold"))
        
        today_date = datetime.now().strftime("%Y-%m-%d")
        DATA_FILE = "quest_data.json"
        
        current_quests = []
        all_data = {} 

        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    all_data = json.load(f)
            except:
                all_data = {}

        user_data = all_data.get(current_username, {})
        last_date = user_data.get("last_active_date")
        stored_quests = user_data.get("daily_quests")

        if last_date == today_date and stored_quests:
            print(f"💾 {current_username}님의 퀘스트 로드")
            current_quests = stored_quests
        else:
            print(f"🌐 {current_username}님의 새 퀘스트 요청")
            try:
                res = requests.get(f"{SERVER_URL}/quests")
                if res.status_code == 200:
                    fetched_quests = res.json()
                    for q in fetched_quests:
                        q['completed'] = False 
                    current_quests = fetched_quests
                    
                    all_data[current_username] = {
                        "last_active_date": today_date,
                        "daily_quests": current_quests
                    }
                    with open(DATA_FILE, "w", encoding="utf-8") as f:
                        json.dump(all_data, f, ensure_ascii=False, indent=4)
                else:
                    quest_list_view.controls.append(ft.Text("서버 에러", color="red"))
                    page.update()
                    return
            except Exception as err:
                print(f"에러: {err}")
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
                    nonlocal current_level

                    if icon_widget.value == "✅": return

                    try:
                        req_data = {
                            "username": current_username, 
                            "difficulty": quest_data['difficulty']
                        }
                        # ⭐ 이전 레벨 저장
                        prev_level = current_level

                        res = requests.post(f"{SERVER_URL}/quests/complete", json=req_data)

                        if res.status_code == 200:
                            result = res.json()

                            icon_widget.value = "✅"

                            new_level = result['new_level']
                            current_xp = result['current_xp']

                            current_level = new_level

                            level_text.value = f"레벨 : Lv{new_level}"
                            xp_text.value = f"경험치: {current_xp} / 100 XP"
                            xp_bar.value = current_xp / 100

                            # ✅ 문자열 말고 레벨 증가로 판별
                            if new_level > prev_level:

                                def close_levelup(e):
                                    levelup_dlg.open = False
                                    page.update()

                                levelup_dlg = ft.AlertDialog(
                                    title=ft.Text("🎉 레벨업 달성!", size=20, weight="bold", color="amber"),
                                    content=ft.Column([
                                        ft.Text(f"축하합니다! {current_username}님!", size=16),
                                        ft.Text(f"Lv.{new_level} 로 성장했습니다!", size=16),
                                        ft.Text(f"현재 경험치: {current_xp}/100", size=12, color="grey"),
                                    ], height=100, tight=True),
                                    actions=[ft.FilledButton("확인", on_click=close_levelup)],
                                )

                                page.overlay.append(levelup_dlg)
                                levelup_dlg.open = True
                                page.update()


                            else:
                                show_message(f"💪 {result.get('message', '퀘스트 완료!')}", "green")

                            # 데이터 저장
                            if os.path.exists(DATA_FILE):
                                with open(DATA_FILE, "r", encoding="utf-8") as f:
                                    current_all_data = json.load(f)
                                
                                if current_username in current_all_data:
                                    current_all_data[current_username]['daily_quests'][index]['completed'] = True
                                    with open(DATA_FILE, "w", encoding="utf-8") as f:
                                        json.dump(current_all_data, f, ensure_ascii=False, indent=4)
                            
                            page.update()
                        else:
                            show_message(f"오류: {res.status_code}", "red")

                    except Exception as err:
                        print(f"에러: {err}") # 터미널에서 에러 확인용
                        show_message("연결 실패", "red")

                card = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(f"🔥 {q['name']}", size=16, weight="bold"),
                            ft.Text(f"목표: {q['count']} | 난이도: {q['difficulty']}", size=12, color="grey"),
                        ]),
                        check_icon 
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor="white10",
                    padding=12,
                    border_radius=10,
                    width=300,
                    on_click=on_card_click 
                )
                quest_list_view.controls.append(card)
        
        page.update()

    # -------------------------------------------------
    # 👶 회원가입 팝업
    # -------------------------------------------------
    def show_signup_modal(e):
        signup_error_text = ft.Text("", color="red", size=12)
        new_id = ft.TextField(label="사용할 아이디", autofocus=True)
        new_pw = ft.TextField(label="사용할 비밀번호", password=True, can_reveal_password=True)

        def close_signup(e):
            signup_dlg.open = False
            page.update()

        def try_signup_enter(e):
            try_signup(e)

        def try_signup(e):
            signup_error_text.value = ""
            page.update()

            if not new_id.value or not new_pw.value:
                signup_error_text.value = "아이디와 비밀번호를 입력해주세요."
                page.update()
                return
            
            signup_data = {"username": new_id.value, "password": new_pw.value, "level": 1, "exp": 0}
            try:
                res = requests.post(f"{SERVER_URL}/users/signup", json=signup_data)
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
            except Exception as err:
                signup_error_text.value = "❌ 연결 실패"
                page.update()

        new_pw.on_submit = try_signup_enter
        signup_dlg = ft.AlertDialog(
            title=ft.Text("회원가입 👶"),
            content=ft.Column([ft.Text("아이디 만들기"), new_id, new_pw, signup_error_text], height=220, tight=True),
            actions=[ft.TextButton("취소", on_click=close_signup), ft.FilledButton("가입하기", on_click=try_signup, style=ft.ButtonStyle(bgcolor="green", color="white"))],
        )
        page.overlay.append(signup_dlg)
        signup_dlg.open = True
        page.update()

    # -------------------------------------------------
    # 🏆 랭킹 & 운동 기록
    # -------------------------------------------------
    def show_ranking(e):
        try:
            res = requests.get(f"{SERVER_URL}/users/ranking")
            if res.status_code == 200:
                rank_list = res.json()
                rank_ui_items = []
                for idx, user in enumerate(rank_list):
                    rank = idx + 1
                    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}위"
                    is_me = (user['username'] == current_username)
                    bg_color = "blue" if is_me else "white10" 
                    rank_ui_items.append(ft.Container(content=ft.Row([ft.Text(f"{medal}"), ft.Text(f"{user['username']}"), ft.Text(f"Lv.{user['level']}")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), padding=10, bgcolor=bg_color, border_radius=10))
                
                def close_rank_overlay(e):
                    rank_dlg.open = False
                    page.update()

                rank_dlg = ft.AlertDialog(
                    title=ft.Text("랭킹"), 
                    content=ft.Column(rank_ui_items, height=300, scroll="auto"), 
                    actions=[ft.TextButton("닫기", on_click=close_rank_overlay)]
                )
                page.overlay.append(rank_dlg)
                rank_dlg.open = True
                page.update()
        except: pass

    def open_record_modal(e):
        nonlocal current_level
        def save_workout_enter(e):
            save_workout(e)
        exercise_input = ft.TextField(label="종목", autofocus=True)
        count_input = ft.TextField(label="횟수", on_submit=save_workout_enter)
        def close_dlg(e):
            dlg.open = False
            page.update()
        def save_workout(e):
            if not exercise_input.value or not count_input.value: return 
            if current_username == "": return
            workout_data = {"username": current_username, "exercise": exercise_input.value, "count": count_input.value}
            try:
                res = requests.post(f"{SERVER_URL}/users/workout", json=workout_data)
                if res.status_code == 200:
                    result = res.json()
                    new_level = result.get('new_level', 1)
                    current_xp = result.get('current_xp', 0)
                    message = result.get('message', '기록 완료!')
                    
                    level_text.value = f"레벨 : Lv{new_level}"
                    xp_text.value = f"경험치: {current_xp} / 100 XP"
                    xp_bar.value = current_xp / 100
                    
                    dlg.title.value = "✅ 기록 성공!"
                    dlg.content.controls.clear()
                    dlg.content.controls.append(ft.Column([ft.Text(message), ft.Container(height=10), ft.ProgressBar(value=current_xp/100, color="orange"), ft.Text(f"Lv.{new_level} (XP: {current_xp}/100)")] ) )
                    dlg.actions.clear()
                    dlg.actions.append(ft.FilledButton("확인", on_click=close_dlg, autofocus=True))
                    page.update()
                else: print(f"실패: {res.text}")
            except Exception as err: print(f"에러: {err}")
        dlg = ft.AlertDialog(title=ft.Text("기록"), content=ft.Column([exercise_input, count_input], height=150, tight=True), actions=[ft.TextButton("취소", on_click=close_dlg), ft.FilledButton("완료", on_click=save_workout)])
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # -------------------------------------------------
    # 🚦 로그인 함수 (수정 완료: 레벨 변수 동기화)
    # -------------------------------------------------
    login_error_text = ft.Text("", color="red")  
    
    def login_click(e):
        global current_username
        nonlocal current_level  # 👈 [핵심] 이 줄이 추가되었습니다!
        
        login_error_text.value = ""
        page.update()

        if not username_input.value or not password_input.value:
            return
            
        data = {"username": username_input.value, "password": password_input.value}
        
        try:
            res = requests.post(f"{SERVER_URL}/users/login", json=data)
            
            if res.status_code == 200:
                result = res.json()
                current_username = result['username']
                user_level = result['level']
                user_xp = result.get('exp', 0)

                current_level = user_level  # 👈 이제 바깥쪽 변수가 진짜로 바뀝니다.
                
                # 화면 초기화
                page.clean()
                
                # 상단 정보 업데이트
                level_text.value = f"레벨 : Lv{user_level}"
                xp_text.value = f"경험치: {user_xp} / 100 XP"
                xp_bar.value = user_xp / 100
                
                page.add(
                    ft.Column([
                        ft.Container(height=20),
                        ft.Text(f"🔥 {current_username} 님!", size=25, weight="bold"),
                        ft.Container(height=10),
                        ft.Row(
                            [
                                level_text, 
                                ft.Column(
                                    [
                                        ft.Container(content=xp_bar, margin=ft.Margin(0, 12, 0, 0)),
                                        xp_text
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2 
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.START, 
                            spacing=15 
                        ),
                        ft.Container(height=15),
                        quest_list_view, 
                        ft.Container(height=10),
                        ft.FilledButton("오늘 운동 기록하기 📝", width=300, height=60, style=ft.ButtonStyle(bgcolor="blue", color="white"), on_click=open_record_modal),
                        ft.Container(height=10), 
                        ft.FilledButton("전체 랭킹 확인하기 🏆", width=300, height=60, style=ft.ButtonStyle(bgcolor="green", color="white"), on_click=show_ranking),
                        ft.Container(height=30),
                    ], 
                    alignment=ft.MainAxisAlignment.START, 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                    )
                )
                page.update()

                try:
                    load_quests() 
                except Exception as e:
                    print(f"퀘스트 로딩 에러: {e}")
                    quest_list_view.controls.append(ft.Text(f"퀘스트 로딩 실패: {e}", color="red"))
                    page.update()

            elif res.status_code == 400:
                try: error_msg = res.json().get('detail', '로그인 실패')
                except: error_msg = "아이디/비번 확인"
                login_error_text.value = f"⚠️ {error_msg}"
                page.update()
            else:
                login_error_text.value = "❌ 서버 오류"
                page.update()

        except Exception as err:
            login_error_text.value = f"연결 에러: {err}"
            page.update()

    # -------------------------------------------------
    # 🏁 초기 화면
    # -------------------------------------------------
    logo = ft.Text("🏋️", size=70)
    username_input = ft.TextField(label="아이디", width=300, autofocus=True)
    password_input = ft.TextField(label="비밀번호", width=300, password=True, on_submit=login_click)
    login_btn = ft.FilledButton("로그인", width=300, height=50, on_click=login_click)
    signup_btn = ft.TextButton("회원가입", on_click=show_signup_modal)

    page.add(ft.Column([ft.Container(height=80), logo, ft.Container(height=20), username_input, password_input, ft.Container(height=10), login_error_text, login_btn, signup_btn], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER))

ft.app(target=main)