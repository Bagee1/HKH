
import cv2
import mediapipe as mp
from multiprocessing import Value
import time

def mouth_detector(is_mouth_open, threshold=0.08):
    mp_face_mesh = mp.solutions.face_mesh

    # Use context manager to manage resources
    with mp_face_mesh.FaceMesh(static_image_mode=False,
                                max_num_faces=1,
                                refine_landmarks=True,
                                min_detection_confidence=0.5,
                                min_tracking_confidence=0.5) as face_mesh:

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open video device.")
            return

        try:
            while True:
                success, frame = cap.read()
                if not success:
                    continue

                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(rgb_frame)

                is_open = False
                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        h, w, _ = frame.shape

                        # Check for necessary landmarks
                        try:
                            upper_lip = face_landmarks.landmark[13]
                            lower_lip = face_landmarks.landmark[14]
                            left_cheek = face_landmarks.landmark[234]
                            right_cheek = face_landmarks.landmark[454]
                        except IndexError:
                            continue

                        y_upper = int(upper_lip.y * h)
                        y_lower = int(lower_lip.y * h)
                        distance = y_lower - y_upper
                        face_width = (right_cheek.x - left_cheek.x) * w

                        if face_width <= 0:
                            continue

                        ratio = distance / face_width
                        is_open = ratio > threshold

                        color = (0, 255, 0) if is_open else (0, 0, 255)
                        cv2.putText(frame, f"Mouth {'Open' if is_open else 'Closed'}", 
                                    (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

                is_mouth_open.value = 1 if is_open else 0

                cv2.imshow("Mouth Detection", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("Mouth detection stopped by user.")
        finally:
            cap.release()
            cv2.destroyAllWindows()
