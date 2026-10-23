
import cv2
import mediapipe as mp
import numpy as np
import csv
import os
import time
from datetime import datetime

# -------------------- CONFIGURATION --------------------

MODEL_PATH = os.path.join("models", "face_landmarker.task")
REPORT_DIR = "reports"
REPORT_FILE = os.path.join(REPORT_DIR, "gaze_events.csv")

DISTRACTION_SECONDS = 3.0

# Eye corner landmark indices
LEFT_EYE = (33, 133)
RIGHT_EYE = (362, 263)

# Iris center landmark indices
LEFT_IRIS_CENTER = 468
RIGHT_IRIS_CENTER = 473

# Gaze thresholds
LEFT_THRESHOLD = 0.42
RIGHT_THRESHOLD = 0.58


# -------------------- CREATE REPORT FOLDER --------------------

os.makedirs(REPORT_DIR, exist_ok=True)


# -------------------- CSV INITIALIZATION --------------------

def initialize_report():
    if not os.path.exists(REPORT_FILE) or os.path.getsize(REPORT_FILE) == 0:
        with open(REPORT_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Event",
                "Start_Time",
                "End_Time",
                "Duration_Seconds"
            ])


def save_event(start_time, end_time, duration):
    initialize_report()

    with open(REPORT_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Possible Gaze Distraction",
            datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S"),
            datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S"),
            round(duration, 2)
        ])

    print(f"[REPORT] Possible gaze distraction: {duration:.2f} seconds")


# -------------------- GAZE ESTIMATION --------------------

def estimate_eye_gaze(landmarks, eye_corners, iris_center):
    """
    Estimate horizontal iris position relative to eye corners.
    Returns LEFT, CENTER, RIGHT, or UNKNOWN.
    """

    try:
        corner_a = np.array([
            landmarks[eye_corners[0]].x,
            landmarks[eye_corners[0]].y
        ])

        corner_b = np.array([
            landmarks[eye_corners[1]].x,
            landmarks[eye_corners[1]].y
        ])

        iris = np.array([
            landmarks[iris_center].x,
            landmarks[iris_center].y
        ])

        eye_width = abs(corner_b[0] - corner_a[0])

        if eye_width < 0.0001:
            return "UNKNOWN"

        # Normalize iris position between the two eye corners.
        ratio = (iris[0] - min(corner_a[0], corner_b[0])) / eye_width

        if ratio < LEFT_THRESHOLD:
            return "LEFT"
        elif ratio > RIGHT_THRESHOLD:
            return "RIGHT"
        else:
            return "CENTER"

    except (IndexError, AttributeError, TypeError):
        return "UNKNOWN"


# -------------------- DRAW LANDMARKS --------------------

def draw_eye_landmarks(frame, landmarks):
    height, width = frame.shape[:2]

    # Draw selected eye and iris landmarks.
    landmark_indices = [
        33, 133, 362, 263,
        468, 473
    ]

    for index in landmark_indices:
        if index < len(landmarks):
            point = landmarks[index]
            x = int(point.x * width)
            y = int(point.y * height)

            cv2.circle(
                frame,
                (x, y),
                3,
                (0, 255, 0),
                -1
            )


# -------------------- MAIN TRACKER --------------------

def main():
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model file not found: {MODEL_PATH}")
        print("Please check that face_landmarker.task is inside the models folder.")
        return

    initialize_report()

    BaseOptions = mp.tasks.BaseOptions
    VisionRunningMode = mp.tasks.vision.RunningMode
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.VIDEO,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )

    # Open the default webcam.
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("[ERROR] Webcam could not be opened.")
        print("Close other apps using the camera and try again.")
        return

    distraction_start = None
    event_saved = False
    start_clock = time.monotonic()
    last_timestamp_ms = -1

    print("[INFO] Gaze tracker started.")
    print("[INFO] Press Q to quit.")

    try:
        with FaceLandmarker.create_from_options(options) as landmarker:
            while True:
                success, frame = camera.read()

                if not success:
                    print("[ERROR] Could not read a frame from the webcam.")
                    break

                # Mirror the camera view for a natural preview.
                frame = cv2.flip(frame, 1)

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb_frame
                )

                timestamp_ms = int(
                    (time.monotonic() - start_clock) * 1000
                )

                # VIDEO mode requires increasing timestamps.
                timestamp_ms = max(timestamp_ms, last_timestamp_ms + 1)
                last_timestamp_ms = timestamp_ms

                result = landmarker.detect_for_video(
                    mp_image,
                    timestamp_ms
                )

                gaze = "NO FACE"

                if result.face_landmarks:
                    landmarks = result.face_landmarks[0]

                    draw_eye_landmarks(frame, landmarks)

                    left_gaze = estimate_eye_gaze(
                        landmarks,
                        LEFT_EYE,
                        LEFT_IRIS_CENTER
                    )

                    right_gaze = estimate_eye_gaze(
                        landmarks,
                        RIGHT_EYE,
                        RIGHT_IRIS_CENTER
                    )

                    if left_gaze == "UNKNOWN" or right_gaze == "UNKNOWN":
                        gaze = "UNKNOWN"
                    elif left_gaze == right_gaze:
                        gaze = left_gaze
                    else:
                        # Different eye estimates are inconclusive.
                        gaze = "UNCERTAIN"

                # Show gaze status.
                status_color = (0, 255, 0)

                if gaze in ("LEFT", "RIGHT"):
                    status_color = (0, 165, 255)
                elif gaze in ("NO FACE", "UNKNOWN", "UNCERTAIN"):
                    status_color = (0, 0, 255)

                cv2.putText(
                    frame,
                    f"Gaze: {gaze}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    status_color,
                    2
                )

                # Count sustained LEFT/RIGHT gaze as a possible event.
                now = time.time()

                if gaze in ("LEFT", "RIGHT"):
                    if distraction_start is None:
                        distraction_start = now
                        event_saved = False

                    duration = now - distraction_start

                    cv2.putText(
                        frame,
                        f"Duration: {duration:.1f}s",
                        (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        status_color,
                        2
                    )

                    if duration >= DISTRACTION_SECONDS and not event_saved:
                        save_event(
                            distraction_start,
                            now,
                            duration
                        )
                        event_saved = True

                else:
                    distraction_start = None
                    event_saved = False

                cv2.putText(
                    frame,
                    "Press Q to quit",
                    (20, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                cv2.imshow("AI Interview Guard - Gaze Tracker", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    except Exception as error:
        print(f"[ERROR] Gaze tracker failed: {error}")

    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("[INFO] Gaze tracker stopped.")
        print(f"[INFO] Report location: {os.path.abspath(REPORT_FILE)}")


if __name__ == "__main__":
    main()
