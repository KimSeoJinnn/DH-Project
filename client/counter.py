import cv2
import mediapipe as mp
import numpy as np
import time

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

cap = cv2.VideoCapture(0)

counter = 0
stage = None
current_mode = "Push-up"

plank_start_time = None

cv2.namedWindow('Helmagotchi AI Trainer', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Helmagotchi AI Trainer', 800, 600)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        key = cv2.waitKey(10) & 0xFF
        if key == ord('1'):
            current_mode = "Push-up"; counter = 0; stage = None
        elif key == ord('2'):
            current_mode = "Sit-up"; counter = 0; stage = None
        elif key == ord('3'):
            current_mode = "Pull-up"; counter = 0; stage = None
        elif key == ord('4'):
            current_mode = "Squat"; counter = 0; stage = None
        elif key == ord('5'):
            current_mode = "Plank"; counter = 0; stage = None; plank_start_time = None
        elif key == ord('q'):
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try:
            landmarks = results.pose_landmarks.landmark

            # ---------------- Push-up ----------------
            if current_mode == "Push-up":
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                angle = calculate_angle(shoulder, elbow, wrist)

                if angle > 160:
                    stage = "up"
                if angle < 90 and stage == 'up':
                    stage = "down"
                    counter += 1

            # ---------------- Sit-up ----------------
            elif current_mode == "Sit-up":
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]

                angle = calculate_angle(shoulder, hip, knee)

                if angle > 130:
                    stage = "down"
                if angle < 70 and stage == 'down':
                    stage = "up"
                    counter += 1

            # ---------------- Pull-up ----------------
            elif current_mode == "Pull-up":
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                angle = calculate_angle(shoulder, elbow, wrist)

                if angle > 150:
                    stage = "down"
                if angle < 70 and stage == 'down':
                    stage = "up"
                    counter += 1

            # ---------------- Squat ----------------
            elif current_mode == "Squat":
                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                angle = calculate_angle(hip, knee, ankle)

                if angle > 160:
                    stage = "up"
                if angle < 90 and stage == 'up':
                    stage = "down"
                    counter += 1

            # ---------------- Plank ----------------
            elif current_mode == "Plank":
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                angle = calculate_angle(shoulder, hip, ankle)

                # 몸이 일직선이면 (160~180도)
                if 160 <= angle <= 180:
                    if plank_start_time is None:
                        plank_start_time = time.time()
                    else:
                        counter = int(time.time() - plank_start_time)
                else:
                    plank_start_time = None

        except:
            pass

        # ---------------- UI ----------------
        # 표시할 텍스트
        mode_text = f"MODE: {current_mode}"
        count_text = f"COUNT: {counter}"

        # 텍스트 크기 계산
        (font_w1, font_h1), _ = cv2.getTextSize(mode_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        (font_w2, font_h2), _ = cv2.getTextSize(count_text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)

        # 박스 크기 계산
        box_width = max(font_w1, font_w2) + 40
        box_height = font_h1 + font_h2 + 60

        # 박스 그리기
        cv2.rectangle(image, (0, 0), (box_width, box_height), (245, 117, 16), -1)

        # 텍스트 출력
        cv2.putText(image, f'MODE: {current_mode}', (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.putText(image, f'COUNT: {counter}', (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

        cv2.putText(image,
                    "1:Push-up 2:Sit-up 3:Pull-up 4:Squat 5:Plank Q:Quit",
                    (10, 550),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 255), 2)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

        cv2.imshow('Helmagotchi AI Trainer', image)

    cap.release()
    cv2.destroyAllWindows()