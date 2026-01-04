import flet as ft
import requests

SERVER_URL = "https://dh-fitness-app.onrender.com"
current_username = "" 

def main(page: ft.Page):
    global current_username
    
    # 📱 1. 앱 기본 설정
    page.title = "헬린이 키우기"
    page.window.width = 400
    page.window.height = 700
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "black"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 메인 화면 갱신용 위젯
    level_text = ft.Text(size=20, color="yellow", weight="bold")
    xp_text = ft.Text(size=14, color="white")
    
    # -------------------------------------------------
    # 👶 2. 회원가입 팝업창
    # -------------------------------------------------
    def show_signup_modal(e):
        # 회원가입에서도 엔터 치면 가입되게 만들기!
        def try_signup_enter(e):
            try_signup(e)

        new_id = ft.TextField(label="사용할 아이디", autofocus=True)
        # 비밀번호 입력하고 엔터치면 -> 가입 시도!
        new_pw = ft.TextField(label="사용할 비밀번호", password=True, can_reveal_password=True, on_submit=try_signup_enter)
        
        def close_signup(e):
            signup_dlg.open = False
            page.update()

        def try_signup(e):
            if not new_id.value or not new_pw.value:
                return
            
            signup_data = {
                "username": new_id.value,
                "password": new_pw.value,
                "level": 1,
                "exp": 0
            }
            
            try:
                res = requests.post(f"{SERVER_URL}/users/signup", json=signup_data)
                
                if res.status_code == 200:
                    signup_dlg.open = False
                    username_input.value = new_id.value 
                    password_input.value = ""
                    password_input.focus() # 바로 비밀번호 입력하게 포커스 이동
                    
                    page.snack_bar = ft.SnackBar(ft.Text("✅ 가입 성공! 로그인 해주세요."), bgcolor="green")
                    page.snack_bar.open = True
                    page.update()
                
                elif res.status_code == 400:
                    page.snack_bar = ft.SnackBar(ft.Text("❌ 이미 존재하는 아이디입니다."), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()
                    
                else:
                    print(f"가입 실패: {res.text}")
                    
            except Exception as err:
                print(f"에러: {err}")
                page.snack_bar = ft.SnackBar(ft.Text("서버 연결 오류"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

        signup_dlg = ft.AlertDialog(
            title=ft.Text("회원가입 👶"),
            content=ft.Column([
                ft.Text("멋진 아이디를 만들어보세요!"),
                new_id,
                new_pw
            ], height=200, tight=True),
            actions=[
                ft.TextButton("취소", on_click=close_signup),
                ft.FilledButton("가입하기", on_click=try_signup, style=ft.ButtonStyle(bgcolor="green", color="white")),
            ],
        )
        page.overlay.append(signup_dlg)
        signup_dlg.open = True
        page.update()

    # -------------------------------------------------
    # 🏆 3. 랭킹 팝업창
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
                    
                    rank_ui_items.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(f"{medal}", size=20),
                                ft.Text(f"{user['username']}", size=16, weight="bold"),
                                ft.Text(f"Lv.{user['level']}", size=14, color="yellow"),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=10,
                            bgcolor=bg_color,
                            border_radius=10
                        )
                    )

                def close_rank(e):
                    rank_dlg.open = False
                    page.update()

                rank_dlg = ft.AlertDialog(
                    title=ft.Text("🏆 명예의 전당"),
                    content=ft.Column(rank_ui_items, height=300, scroll="auto"),
                    actions=[ft.TextButton("닫기", on_click=close_rank)],
                )
                page.overlay.append(rank_dlg)
                rank_dlg.open = True
                page.update()
            else:
                print("랭킹 불러오기 실패")
        except Exception as err:
            print(f"에러: {err}")

    # -------------------------------------------------
    # 🏋️ 4. 운동 기록 로직
    # -------------------------------------------------
    def open_record_modal(e):
        # 여기도 엔터키 기능 추가!
        def save_workout_enter(e):
            save_workout(e)

        exercise_input = ft.TextField(label="종목", autofocus=True)
        # 횟수 입력하고 엔터치면 -> 기록 완료!
        count_input = ft.TextField(label="횟수", on_submit=save_workout_enter)

        def close_dlg(e):
            dlg.open = False
            page.update()

        def save_workout(e):
            if not exercise_input.value or not count_input.value: return 
            if current_username == "": return

            workout_data = {
                "username": current_username,
                "exercise": exercise_input.value,
                "count": count_input.value
            }

            try:
                res = requests.post(f"{SERVER_URL}/users/workout", json=workout_data)
                if res.status_code == 200:
                    result = res.json()
                    new_level = result.get('new_level', 1)
                    current_xp = result.get('current_xp', 0)
                    message = result.get('message', '기록 완료!')

                    level_text.value = f"현재 레벨: Lv.{new_level}"
                    xp_text.value = f"경험치: {current_xp} / 100 XP"
                    
                    dlg.title.value = "✅ 기록 성공!"
                    dlg.content.controls.clear()
                    dlg.content.controls.append(
                        ft.Column([
                            ft.Text(message, size=16),
                            ft.Container(height=10),
                            ft.ProgressBar(value=current_xp/100, color="orange", bgcolor="grey"),
                            ft.Text(f"Lv.{new_level} (XP: {current_xp}/100)", size=14, color="orange")
                        ])
                    )
                    dlg.actions.clear()
                    dlg.actions.append(ft.FilledButton("확인", on_click=close_dlg, autofocus=True)) # 확인 버튼에 포커스
                    page.update()
                else:
                    print(f"실패: {res.text}")
            except Exception as err:
                print(f"에러: {err}")

        dlg = ft.AlertDialog(
            title=ft.Text("퀘스트 기록 📝"),
            content=ft.Column([exercise_input, count_input], height=150, tight=True),
            actions=[
                ft.TextButton("취소", on_click=close_dlg),
                ft.FilledButton("기록 완료", on_click=save_workout, style=ft.ButtonStyle(bgcolor="blue", color="white")),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # -------------------------------------------------
    # 🚦 5. 로그인 로직
    # -------------------------------------------------
    def login_click(e):
        global current_username
        if not username_input.value or not password_input.value: return

        data = {"username": username_input.value, "password": password_input.value}
        
        try:
            login_btn.disabled = True
            login_btn.text = "로그인 중..."
            page.update()

            res = requests.post(f"{SERVER_URL}/users/login", json=data)
            
            if res.status_code == 200:
                result = res.json()
                current_username = result['username']
                user_level = result['level']
                user_xp = result.get('exp', 0) 
                
                page.clean() 
                level_text.value = f"현재 레벨: Lv.{user_level}"
                xp_text.value = f"경험치: {user_xp} / 100 XP"

                page.add(
                    ft.Column(
                        [
                            ft.Container(height=50), 
                            ft.Text(f"🔥 {current_username}님, 어서오세요!", size=25, weight="bold"),
                            level_text, xp_text,
                            ft.Container(height=40), 
                            
                            ft.FilledButton("오늘 운동 기록하기 📝", width=300, height=60, style=ft.ButtonStyle(bgcolor="blue", color="white"), on_click=open_record_modal),
                            ft.Container(height=15), 
                            
                            ft.FilledButton("전체 랭킹 확인하기 🏆", width=300, height=60, style=ft.ButtonStyle(bgcolor="green", color="white"), on_click=show_ranking),
                            ft.Container(height=50),
                            ft.Text("💪", size=80),
                            ft.Text("꾸준함이 답이다!", size=14, color="grey"),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                )
                page.update()
            else:
                login_btn.disabled = False
                login_btn.text = "로그인 실패"
                page.update()
        except Exception as err:
            print(f"에러: {err}")
            login_btn.disabled = False
            login_btn.text = "서버 에러"
            page.update()

    # -------------------------------------------------
    # 🏁 6. 초기 화면 (로그인 창)
    # -------------------------------------------------
    logo = ft.Text("🏋️", size=70)
    title = ft.Text("헬린이 키우기", size=28, weight="bold")
    
    # ★ [핵심] 비밀번호 입력하고 엔터치면 -> 로그인 함수 실행!
    username_input = ft.TextField(label="아이디", width=300, autofocus=True) # 앱 켜면 아이디창에 바로 커서
    password_input = ft.TextField(label="비밀번호", width=300, password=True, can_reveal_password=True, on_submit=login_click)
    
    login_btn = ft.FilledButton("로그인", width=300, height=50, on_click=login_click)
    signup_btn = ft.TextButton("계정이 없으신가요? 회원가입", on_click=show_signup_modal)

    page.add(
        ft.Column(
            [
                ft.Container(height=80), 
                logo, ft.Container(height=20), title, ft.Container(height=50),
                username_input, password_input, 
                ft.Container(height=20), login_btn,
                ft.Container(height=10), signup_btn 
            ],
            alignment=ft.MainAxisAlignment.START, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
            expand=True
        )
    )

ft.app(target=main)