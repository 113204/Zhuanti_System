import cv2
import threading
import datetime
import time
import cv2
import mediapipe as mp
import numpy as np
import winsound
import datetime
import time
import cv2
import mediapipe as mp
import numpy as np
import winsound
import pyttsx3
from PIL import ImageFont, ImageDraw, Image


from views.user_views import logger

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

begin = []
start = []
danger = []
freq = 2000
duration = 5000


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle
    return angle


def add_chinese(img, text, left, top, textcolor=(0, 255, 0), textsize=20):
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    font_text = ImageFont.truetype("font/simsun.ttc", textsize, encoding="utf-8")
    draw.text((left, top), text, textcolor, font=font_text)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


def start_speaking_thread(text):
    def speak_text(event, text):
        engine = pyttsx3.init()
        while not event.is_set():
            engine.say(text)
            engine.runAndWait()
            time.sleep(1)  # Adjust the interval as needed

    stop_event = threading.Event()
    thread = threading.Thread(target=speak_text, args=(stop_event, text))
    thread.start()
    return stop_event, thread


class Posedetect(object):

    def __init__(self, session):
        self.session = session
        self.video = cv2.VideoCapture(1)
        (self.grabbed, self.frame) = self.video.read()
        self.pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.started_time = 0
        self.counter = 0
        self.stage = 'up'
        self.join_color = (203, 192, 255)
        self.color = (0, 255, 0)
        self.warning_message = ''
        self.exercise_time = datetime.datetime.now().replace(microsecond=0)
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()
        cv2.destroyAllWindows()

    def check_login(self):
        email = self.session.get('email')
        return email is not None  # 登入True 反之False
    def stop(self):
        self.video.release() 

    def get_frame(self):
        img = self.frame
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img.flags.writeable = False
        results = self.pose.process(img)
        img.flags.writeable = True
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        try:

            landmarks = results.pose_landmarks.landmark

            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                              landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                           landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                           landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
            right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                           landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

            left_shoulder_angle = calculate_angle(left_hip, left_shoulder, left_elbow)
            left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
            left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)

            right_shoulder_angle = calculate_angle(right_hip, right_shoulder, right_elbow)
            right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
            right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)

            if right_elbow_angle > 150 and right_shoulder_angle > 150:
                if len(start) == 0:
                    start_time = time.time()
                    start.append(start_time)
                self.started_time = time.time() - start[0]

            elif right_elbow_angle < 150 and self.started_time < 3:
                start.clear()

            if len(begin) == 0:
                begin_time = datetime.datetime.now().replace(microsecond=0)
                begin.append(begin_time)
            self.exercise_time = datetime.datetime.now().replace(microsecond=0) - begin[0]

            if int(self.started_time) == 1:
                show_time = 3
                cv2.putText(img, str(show_time), (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 6, (255, 255, 255), 7,
                            cv2.LINE_AA)
            elif int(self.started_time) == 2:
                show_time = 2
                cv2.putText(img, str(show_time), (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 6, (255, 255, 255), 7,
                            cv2.LINE_AA)
            elif int(self.started_time) == 3:
                show_time = 1
                cv2.putText(img, str(show_time), (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 6, (255, 255, 255), 7,
                            cv2.LINE_AA)
            else:
                show_time = ''
                cv2.putText(img, str(show_time), (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 6, (255, 255, 255), 7,
                            cv2.LINE_AA)

            if self.started_time > 3:
                if right_elbow_angle < 30 and left_elbow_angle < 30:

                    self.warning_message = '請將雙手向外握一點'
                    self.joint_color = (0, 255, 255)
                    self.color = (0, 255, 255)

                    if len(danger) == 0:
                        danger_time = time.time()
                        danger.append(danger_time)
                    die_time = time.time() - danger[0]

                    if die_time > 10.3:
                        die_message = 'WARNING!'
                        self.joint_color = (0, 0, 255)
                        self.color = (0, 0, 255)
                        cv2.rectangle(img, (80, 100), (550, 200), (0, 0, 255), -1)
                        cv2.putText(img, str(die_message), (100, 180), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 8,
                                    cv2.LINE_AA)
                        if die_time > 10.5:
                            winsound.Beep(freq, duration)
                            # cap.release()
                            # cv2.destroyAllWindows()

                    elif die_time > 10:
                        self.joint_color = (0, 0, 255)
                        self.color = (0, 0, 255)

                    elif die_time > 7:
                        self.joint_color = (0, 133, 242)
                        self.color = (0, 133, 242)

                elif right_elbow_angle < 30:
                    self.warning_message = '請將右手向外握一點'
                    self.joint_color = (0, 255, 255)
                    self.color = (0, 255, 255)

                elif left_elbow_angle < 30:
                    self.warning_message = '請將左手向外握一點'
                    self.joint_color = (0, 255, 255)
                    self.color = (0, 255, 255)

                elif 30 < right_elbow_angle < 50 and right_shoulder_angle < 60 and 30 < left_elbow_angle < 50 and left_shoulder_angle < 60:
                    danger.clear()
                    self.stage = 'down'
                    self.warning_message = ''
                    self.joint_color = (203, 192, 255)
                    self.color = (0, 255, 0)

                elif 50 < right_elbow_angle < 150 and right_shoulder_angle > 60 and 50 < left_elbow_angle < 150 and left_shoulder_angle > 60:
                    self.stage = 'null'
                    self.warning_message = ''
                    self.joint_color = (203, 192, 255)
                    self.color = (0, 255, 0)

                if self.stage == 'down' and right_shoulder_angle < 30 and left_shoulder_angle < 30:
                    self.warning_message = '請將肩膀向外打開一點'
                    self.joint_color = (0, 255, 255)
                    self.color = (0, 255, 255)

                elif self.stage == 'down' and right_shoulder_angle < 30:
                    self.warning_message = '請將右肩向外打開一點'
                    self.joint_color = (0, 255, 255)
                    self.color = (0, 255, 255)

                elif self.stage == 'down' and left_shoulder_angle < 30:
                    self.warning_message = '請將左肩向外打開一點'
                    self.joint_color = (0, 255, 255)
                    self.color = (0, 255, 255)

                elif self.stage == 'down' and right_shoulder_angle > 60 and left_shoulder_angle > 60:
                    self.warning_message = '請將肩膀向內縮一點'
                    self.joint_color = (0, 255, 255)
                    self.color = (0, 255, 255)

                elif self.stage == 'down' and right_shoulder_angle > 60:
                    self.warning_message = '請將右肩向內縮一點'
                    self.joint_color = (0, 255, 255)
                    self.color = (0, 255, 255)

                elif self.stage == 'down' and left_shoulder_angle > 60:
                    self.warning_message = '請將左肩向內縮一點'
                    self.joint_color = (0, 255, 255)
                    self.color = (0, 255, 255)

                elif self.stage == 'down' and right_elbow_angle > 50 and left_elbow_angle > 50:
                    self.warning_message = '請將雙手向內握一點'
                    self.joint_color = (0, 255, 255)
                    self.color = (0, 255, 255)

                elif self.stage == 'down' and right_elbow_angle > 50:
                    self.warning_message = '請將右手向內握一點'
                    self.joint_color = (0, 255, 255)
                    self.color = (0, 255, 255)

                elif self.stage == 'down' and left_elbow_angle > 50:
                    self.warning_message = '請將左手向內握一點'
                    self.joint_color = (0, 255, 255)
                    self.color = (0, 255, 255)

                if right_elbow_angle > 150 and left_elbow_angle > 150 and self.stage == 'null':
                    self.stage = 'up'
                    self.warning_message = ''
                    self.counter += 1
                    self.joint_color = (203, 192, 255)
                    self.color = (0, 255, 0)

                print(self.stage)

                self.stop_event, self.thread = start_speaking_thread(self.warning_message)

                mp_drawing.draw_landmarks(
                    img,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=self.joint_color, thickness=5, circle_radius=1),
                    mp_drawing.DrawingSpec(color=self.color, thickness=2, circle_radius=2),
                    # landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                )

                cv2.rectangle(img, (0, 0), (140, 40), (255, 0, 0), -1)
                cv2.rectangle(img, (0, 40), (650, 80), (0, 255, 255), -1)
                cv2.rectangle(img, (585, 0), (650, 40), (0, 0, 255), -1)
                cv2.putText(img, str(self.exercise_time), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
                            cv2.LINE_AA)
                # cv2.putText(img, str(self.warning_message), (90, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(img, str(self.counter), (590, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

                cv2.putText(img, str(int(left_elbow_angle)), tuple(np.multiply(left_elbow, [640, 480]).astype(int)),
                            cv2.FONT_ITALIC, 1, (0, 0, 255), 2)
                cv2.putText(img, str(int(left_shoulder_angle)),
                            tuple(np.multiply(left_shoulder, [640, 480]).astype(int)),
                            cv2.FONT_ITALIC, 1, (0, 0, 255), 2)
                cv2.putText(img, str(int(left_knee_angle)), tuple(np.multiply(left_knee, [640, 480]).astype(int)),
                            cv2.FONT_ITALIC, 1, (0, 0, 255), 2)
                cv2.putText(img, str(int(right_elbow_angle)), tuple(np.multiply(right_elbow, [640, 480]).astype(int)),
                            cv2.FONT_ITALIC, 1, (0, 0, 255), 2)
                cv2.putText(img, str(int(right_shoulder_angle)),
                            tuple(np.multiply(right_shoulder, [640, 480]).astype(int)),
                            cv2.FONT_ITALIC, 1, (0, 0, 255), 2)
                cv2.putText(img, str(int(right_knee_angle)), tuple(np.multiply(right_knee, [640, 480]).astype(int)),
                            cv2.FONT_ITALIC, 1, (0, 0, 255), 2)
                img = add_chinese(img, self.warning_message, 130, 40, (255, 0, 0), 40)

            elif len(start) == 0:
                self.warning_message = ''
                begin.clear()
                empty = datetime.datetime.now().replace(microsecond=0) - datetime.datetime.now().replace(microsecond=0)
                self.exercise_time = empty

                # mp_drawing.draw_landmarks(
                #     img,
                #     results.pose_landmarks,
                #     mp_pose.POSE_CONNECTIONS,
                #     mp_drawing.DrawingSpec(color=(203, 192, 255), thickness=5, circle_radius=1),
                #     mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                #     # landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                # )

                # cv2.rectangle(img, (0, 0), (140, 40), (255, 0, 0), -1)
                # cv2.rectangle(img, (0, 40), (650, 80), (0, 255, 255), -1)
                # cv2.rectangle(img, (585, 0), (650, 40), (0, 0, 255), -1)
                # cv2.putText(img, str(self.exercise_time), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
                #             cv2.LINE_AA)
                # cv2.putText(img, str(self.warning_message), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                # cv2.putText(img, str(self.counter), (590, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            else:
                self.warning_message = ''
                begin.clear()
                empty = datetime.datetime.now().replace(microsecond=0) - datetime.datetime.now().replace(microsecond=0)
                self.exercise_time = empty
                mp_drawing.draw_landmarks(
                    img,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(203, 192, 255), thickness=5, circle_radius=1),
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    # landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                )

        except Exception as e:
            print(f'發生錯誤: {e}')

        ret, jpeg = cv2.imencode('.jpg', img)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()
