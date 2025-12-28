import flet as ft
import requests

SERVER_URL = "https://dh-fitness-app.onrender.com"
current_username = "" 

def main(page: ft.Page):
    global current_username
    
    page.title = "헬린이 키우기"
    page.window.width = 400
    page.window.height = 700
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "black"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    level_text = ft.Text(size=20, color="yellow", weight="bold")
    xp_text = ft.Text(size=14, color="white")
    
    # -------------------------------------------------
    # 1. 🏆 랭킹 팝업창 (에러 수정됨!)
    # -------------------------------------------------
    def show_ranking(e):
        try:
            res = requests.get(f"{SERVER_URL}/users/ranking")
            if res.status_code == 200:
                rank_list = res.json()
                
                # 랭킹 리스트 만들기 (UI)
                rank_ui_items = []
                for idx, user in enumerate(rank_list):
                    rank = idx + 1
                    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}위"
                    
                    # 내 아이디면 색깔 다르게 표시
                    is_me = (user['username'] == current_username)
                    
                    # ★ [수정] 에러나던 ft.colors... 제거하고 단순한 문자열 사용!
                    # "blue" = 파란색, "white10" = 투명한 흰색
                    bg_color = "blue" if is_me else "white10" 
                    
                    rank_ui_items.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(f"{medal}", size=20),
                                ft.Text(f"{user['username']}", size=16, weight="bold"),
                                ft.Text(f"Lv.{user['level']}", size=14, color="yellow"),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=10,
                            bgcolor=bg_color, # 수정된 색상 적용
                            border_radius=10
                        )
                    )

                # 닫기 함수
                def close_rank(e):
                    rank_dlg.open = False
                    page.update()

                # 팝업 조립
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
    # 2. 🏋️ 운동 기록 로직
    # -------------------------------------------------
    def open_record_modal(e):
        exercise_input = ft.TextField(label="종목", autofocus=True)
        count_input = ft.TextField(label="횟수")

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

                    # 메인 화면 갱신
                    level_text.value = f"현재 레벨: Lv.{new_level}"
                    xp_text.value = f"경험치: {current_xp} / 100 XP"
                    
                    # 팝업 내용 변경
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
                    dlg.actions.append(ft.FilledButton("확인", on_click=close_dlg))
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
    # 3. 🚦 로그인 로직
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
                            
                            ft.FilledButton(
                                "오늘 운동 기록하기 📝", width=300, height=60,
                                style=ft.ButtonStyle(bgcolor="blue", color="white"),
                                on_click=open_record_modal 
                            ),
                            ft.Container(height=15), 
                            
                            ft.FilledButton(
                                "전체 랭킹 확인하기 🏆", width=300, height=60,
                                style=ft.ButtonStyle(bgcolor="green", color="white"),
                                on_click=show_ranking 
                            ),
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

    # 초기 화면
    logo = ft.Text("🏋️", size=70)
    title = ft.Text("헬린이 키우기", size=28, weight="bold")
    username_input = ft.TextField(label="아이디", width=300)
    password_input = ft.TextField(label="비밀번호", width=300, password=True, can_reveal_password=True)
    login_btn = ft.FilledButton("로그인", width=300, height=50, on_click=login_click)

    page.add(
        ft.Column(
            [ft.Container(height=80), logo, ft.Container(height=20), title, ft.Container(height=50),
             username_input, password_input, ft.Container(height=20), login_btn],
            alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True
        )
    )

# 경고 메시지(Deprecation)는 무시하셔도 됩니다. 실행에는 문제 없습니다!
ft.app(target=main)