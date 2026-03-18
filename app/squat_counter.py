import cv2
import mediapipe as mp
import numpy as np
import time  # ★ 추가: 시간 측정을 위한 라이브러리
import sys

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))

    return np.degrees(angle)

cap = cv2.VideoCapture(0)

counter = 0
stage = "-"
standing_hip_y = 0 
last_rep_time = 0  # ★ 추가: 마지막으로 스쿼트를 성공한 시간을 기록할 변수
# 명령줄 인자로 목표 횟수가 전달되면 사용하고, 아니면 기본값 10으로 설정
TARGET_COUNT = int(sys.argv[1]) if len(sys.argv) > 1 else 10

with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as pose:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        results = pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try:
            landmarks = results.pose_landmarks.landmark

            hip = [
                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y
            ]

            knee = [
                landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y
            ]

            ankle = [
                landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y
            ]

            angle = calculate_angle(hip, knee, ankle)
            current_hip_y = hip[1]

            # 1. 서 있을 때
            if angle > 160:
                stage = "down"
                standing_hip_y = current_hip_y

            # 2. 앉았을 때 (각도 조건 + Y좌표 조건 + ★시간 조건★)
            if angle < 90 and stage == "down":
                if current_hip_y > standing_hip_y + 0.08:  # 몸이 충분히 내려갔는지 확인
                    current_time = time.time()  # 현재 시간 측정
                    
                    # 마지막 성공 시간으로부터 1초(1.0) 이상 지났는지 확인
                    if current_time - last_rep_time > 1.0: 
                        stage = "up"
                        counter += 1
                        last_rep_time = current_time  # 성공 시간을 현재 시간으로 갱신
                        print(f"현재 스쿼트 개수: {counter}개")
                        
                        # 목표 개수 달성 시 자동 종료 (성공 코드 0 반환)
                        if counter >= TARGET_COUNT:
                            print("🎉 목표 달성! 카메라를 종료합니다.")
                            cap.release()
                            cv2.destroyAllWindows()
                            exit(0)
                    else:
                        # 1초도 안 돼서 또 앉았다면? 너무 빠르다고 경고
                        cv2.putText(image, "TOO FAST!", (200, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                else:
                    # 각도만 굽히고 몸은 안 내려갔다면? 가짜 동작 경고
                    cv2.putText(image, "FAKE DETECTED!", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        except:
            pass

        # 스쿼트 횟수 화면 출력
        cv2.putText(image, f'COUNT: {counter} / {TARGET_COUNT}', (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        
        # 현재 상태 화면 출력
        cv2.putText(image, f'STAGE: {stage}', (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.imshow('Squat Counter', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            exit(1)  # 목표를 못 채우고 q를 누르면 에러 코드(1) 반환
            break

cap.release()
cv2.destroyAllWindows()
exit(1) # 끝까지 와도 목표를 못 채웠으면 실패(1) 반환