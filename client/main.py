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
    current_title = "입문자"
    
    page.title = "헬린이 키우기 (Developer Mode)"
    page.window.width = 400
    page.window.height = 700 
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "black"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 경로 설정
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    DATA_FILE = os.path.join(script_dir, "quest_data.json")
    print(f"📂 데이터 저장 위치: {DATA_FILE}")

    # UI 컴포넌트
    level_text = ft.Text(value="Lv. 1 입문자", size=20, color="yellow", weight="bold")
    xp_text = ft.Text(size=12, color="white")
    xp_bar = ft.ProgressBar(width=300, color="orange", bgcolor="grey", value=0)
    
    quest_list_view = ft.Column(spacing=10, scroll="auto", height=280)

    # -------------------------------------------------
    # 메시지 함수
    # -------------------------------------------------
    def show_message(msg, color="green"):
        snack = ft.SnackBar(content=ft.Text(msg, color="white", weight="bold"), bgcolor=color, duration=2000)
        page.snack_bar = snack
        snack.open = True
        page.update()

    # -------------------------------------------------
    # [개발자용] 경험치 치트키 함수
    # -------------------------------------------------
    def debug_add_xp(e, amount):
        nonlocal current_level
        if not current_username:
            show_message("로그인 먼저 하세요!", "red")
            return

        try:
            # 아까 서버에서 수정한 'amount' 필드를 사용
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
                
                # UI 갱신
                current_level = new_level
                level_text.value = f"Lv.{new_level} {new_title}"
                xp_text.value = f"경험치: {current_xp} / 100 XP"
                xp_bar.value = current_xp / 100
                
                show_message(f"🧪 테스트: 경험치 {amount} 추가됨!", "blue")
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
                    nonlocal current_level
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
                            current_level = new_level

                            level_text.value = f"Lv.{new_level} {new_title}"
                            xp_text.value = f"경험치: {current_xp} / 100 XP"
                            xp_bar.value = current_xp / 100

                            if new_level > prev_level:
                                def close_levelup(e):
                                    levelup_dlg.open = False
                                    page.update()
                                levelup_dlg = ft.AlertDialog(
                                    title=ft.Text("🎉 레벨업!", size=20, color="amber"),
                                    content=ft.Column([
                                        ft.Text(f"Lv.{new_level} 달성!"),
                                        ft.Text(f"이제 [{new_title}] 입니다!", color="green", weight="bold"),
                                    ], height=100, tight=True),
                                    actions=[ft.FilledButton("확인", on_click=close_levelup)],
                                )
                                page.overlay.append(levelup_dlg)
                                levelup_dlg.open = True
                            else:
                                show_message(f"💪 {result.get('message', '완료!')}", "green")

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
    # 회원가입 / 랭킹 (생략 없이 포함)
    # -------------------------------------------------
    def show_signup_modal(e):
        new_id = ft.TextField(label="ID", autofocus=True)
        new_pw = ft.TextField(label="PW", password=True)
        signup_error = ft.Text("", color="red")
        def do_signup(e):
            if not new_id.value or not new_pw.value: return
            try:
                res = requests.post(f"{SERVER_URL}/users/signup", json={"username": new_id.value, "password": new_pw.value})
                if res.status_code == 200:
                    signup_dlg.open = False
                    login_error_text.value = "가입 완료! 로그인하세요."
                    login_error_text.color = "green"
                    page.update()
                else:
                    signup_error.value = "이미 있는 아이디입니다."
                    page.update()
            except: signup_error.value = "연결 실패"
            page.update()
        
        signup_dlg = ft.AlertDialog(title=ft.Text("회원가입"), content=ft.Column([new_id, new_pw, signup_error], height=150), actions=[ft.FilledButton("가입", on_click=do_signup)])
        page.overlay.append(signup_dlg)
        signup_dlg.open = True
        page.update()

    def show_ranking(e):
        try:
            res = requests.get(f"{SERVER_URL}/users/ranking")
            if res.status_code == 200:
                rank_ui = []
                for i, u in enumerate(res.json()):
                    rank_ui.append(ft.Container(content=ft.Row([ft.Text(f"{i+1}위 {u['username']}"), ft.Text(f"Lv.{u['level']}")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), padding=10, bgcolor="white10", border_radius=5))
                dlg = ft.AlertDialog(title=ft.Text("랭킹"), content=ft.Column(rank_ui, height=200, scroll="auto"), actions=[ft.TextButton("닫기", on_click=lambda e: setattr(dlg, 'open', False) or page.update())])
                page.overlay.append(dlg)
                dlg.open = True
                page.update()
        except: pass

    # -------------------------------------------------
    # 로그인 (치트키 버튼 추가됨)
    # -------------------------------------------------
    login_error_text = ft.Text("", color="red")  
    
    def login_click(e):
        global current_username
        nonlocal current_level
        if not username_input.value or not password_input.value: return
        
        try:
            res = requests.post(f"{SERVER_URL}/users/login", json={"username": username_input.value, "password": password_input.value})
            if res.status_code == 200:
                data = res.json()
                current_username = data['username']
                current_level = data['level']
                user_title = data.get('title', '초보자')
                
                level_text.value = f"Lv.{current_level} {user_title}"
                xp_text.value = f"경험치: {data.get('exp', 0)} / 100 XP"
                xp_bar.value = data.get('exp', 0) / 100
                xp_bar.width = 300

                page.clean()
                page.add(ft.Column([
                    ft.Container(height=20),
                    ft.Text(f"🔥 {current_username} 님!", size=25, weight="bold"),
                    ft.Container(height=20),
                    level_text, 
                    ft.Container(height=10),
                    xp_bar, xp_text,
                    
                    # 🛠️ [개발자용 버튼 구역]
                    ft.Container(height=10),
                    ft.Row([
                        ft.FilledButton("🧪 +25 XP", on_click=lambda e: debug_add_xp(e, 25), style=ft.ButtonStyle(bgcolor="grey")),
                        ft.FilledButton("🧪 +95 XP", on_click=lambda e: debug_add_xp(e, 95), style=ft.ButtonStyle(bgcolor="red")),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    
                    ft.Container(height=20),
                    quest_list_view,
                    ft.Container(height=10),
                    ft.FilledButton("랭킹 보기 🏆", width=300, height=50, style=ft.ButtonStyle(bgcolor="green", color="white"), on_click=show_ranking)
                ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
                
                page.update()
                load_quests()
            else:
                login_error_text.value = "로그인 실패"
                page.update()
        except Exception as err:
            login_error_text.value = f"에러: {err}"
            page.update()

    username_input = ft.TextField(label="ID", width=300)
    password_input = ft.TextField(label="PW", width=300, password=True, on_submit=login_click)
    
    page.add(ft.Column([
        ft.Container(height=50), ft.Text("🏋️", size=70),
        username_input, password_input, login_error_text,
        ft.FilledButton("로그인", width=300, height=50, on_click=login_click),
        ft.TextButton("회원가입", on_click=show_signup_modal)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER))

ft.app(target=main)