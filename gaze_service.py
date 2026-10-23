
import os
import time
import threading

import cv2
import mediapipe as mp
import numpy as np


# ==================================================
# CONFIGURATION
# ==================================================

MODEL_PATH = os.path.join("models", "face_landmarker.task")

LEFT_EYE = (33, 133)
RIGHT_EYE = (362, 263)

LEFT_IRIS_CENTER = 468
RIGHT_IRIS_CENTER = 473

LEFT_EYE_VERTICAL = (159, 145)
RIGHT_EYE_VERTICAL = (386, 374)

# Horizontal thresholds
LEFT_THRESHOLD = 0.42
RIGHT_THRESHOLD = 0.58

# Vertical thresholds: more sensitive
UP_THRESHOLD = 0.45
DOWN_THRESHOLD = 0.55

# Record a possible event after this many seconds
DISTRACTION_SECONDS = 3.0

DISTRACTION_DIRECTIONS = {
    "LEFT",
    "RIGHT",
    "UP",
    "DOWN",
    "UP-LEFT",
    "UP-RIGHT",
    "DOWN-LEFT",
    "DOWN-RIGHT",
}


# ==================================================
# GAZE SERVICE
# ==================================================

class GazeService:

    def __init__(self):
        self.lock = threading.Lock()
        self.landmarker = None

        self.distraction_start = None
        self.event_saved = False
        self.events = []
                # Analytics dashboard statistics
        self.session_start_time = None
        self.gaze_counts = {
            "LEFT": 0,
            "RIGHT": 0,
            "UP": 0,
            "DOWN": 0,
            "CENTER": 0,
            "OTHER": 0
        }
        self.total_frames_processed = 0

        self.status = {
            "gaze": "NOT STARTED",
            "face_detected": False,
            "message": "Start the webcam to begin monitoring.",
            "distraction_seconds": 0.0,
            "event_count": 0,
            "horizontal_ratio": None,
            "vertical_ratio": None,
        }

        self.last_timestamp_ms = 0
                # Analytics session tracking
        self.session_start_time = None

        self.gaze_counts = {
            "LEFT": 0,
            "RIGHT": 0,
            "UP": 0,
            "DOWN": 0,
            "CENTER": 0,
            "OTHER": 0
        }

        self.total_frames_processed = 0

    # --------------------------------------------------
    # START MONITORING
    # --------------------------------------------------

    def start(self):

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"MediaPipe model not found: {MODEL_PATH}"
            )

        if self.landmarker is not None:
            return

        base_options = mp.tasks.BaseOptions
        vision = mp.tasks.vision

        options = vision.FaceLandmarkerOptions(
            base_options=base_options(
                model_asset_path=MODEL_PATH
            ),
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.landmarker = (
            vision.FaceLandmarker.create_from_options(options)
        )

        self.distraction_start = None
        self.event_saved = False
        self.last_timestamp_ms = 0

        with self.lock:
            self.status = {
                "gaze": "WAITING",
                "face_detected": False,
                "message": "Monitoring started. Looking for a face.",
                "distraction_seconds": 0.0,
                "event_count": len(self.events),
                "horizontal_ratio": None,
                "vertical_ratio": None,
            }

    # --------------------------------------------------
    # ESTIMATE GAZE FOR ONE EYE
    # --------------------------------------------------

    @staticmethod
    def estimate_gaze(
        landmarks,
        eye_corners,
        iris_center,
        vertical_points,
    ):

        try:
            # Horizontal iris position
            corner_a = landmarks[eye_corners[0]].x
            corner_b = landmarks[eye_corners[1]].x
            iris_x = landmarks[iris_center].x

            eye_width = abs(corner_b - corner_a)

            if eye_width < 0.0001:
                return "UNKNOWN", "UNKNOWN", None, None

            horizontal_ratio = (
                (iris_x - min(corner_a, corner_b))
                / eye_width
            )

            if horizontal_ratio < LEFT_THRESHOLD:
                horizontal = "LEFT"
            elif horizontal_ratio > RIGHT_THRESHOLD:
                horizontal = "RIGHT"
            else:
                horizontal = "CENTER"

            # Vertical iris position
            upper_y = landmarks[vertical_points[0]].y
            lower_y = landmarks[vertical_points[1]].y
            iris_y = landmarks[iris_center].y

            eye_height = abs(lower_y - upper_y)

            if eye_height < 0.0001:
                return (
                    horizontal,
                    "UNKNOWN",
                    round(horizontal_ratio, 3),
                    None,
                )

            # Normalize iris position inside the eye opening
            vertical_ratio = (
                (iris_y - min(upper_y, lower_y))
                / eye_height
            )

            if vertical_ratio < UP_THRESHOLD:
                vertical = "UP"
            elif vertical_ratio > DOWN_THRESHOLD:
                vertical = "DOWN"
            else:
                vertical = "CENTER"

            return (
                horizontal,
                vertical,
                round(horizontal_ratio, 3),
                round(vertical_ratio, 3),
            )

        except (IndexError, AttributeError, TypeError):
            return "UNKNOWN", "UNKNOWN", None, None

    # --------------------------------------------------
    # COMBINE BOTH EYE ESTIMATES
    # --------------------------------------------------

    @staticmethod
    def combine_eye_estimates(left_value, right_value):

        if left_value == "UNKNOWN" or right_value == "UNKNOWN":
            return "UNKNOWN"

        if left_value == right_value:
            return left_value

        if left_value == "CENTER":
            return right_value

        if right_value == "CENTER":
            return left_value

        return "UNCERTAIN"

    @staticmethod
    def combine_directions(horizontal, vertical):

        if "UNKNOWN" in (horizontal, vertical):
            return "UNKNOWN"

        if "UNCERTAIN" in (horizontal, vertical):
            return "UNCERTAIN"

        if horizontal == "CENTER" and vertical == "CENTER":
            return "CENTER"

        if horizontal == "CENTER":
            return vertical

        if vertical == "CENTER":
            return horizontal

        return f"{vertical}-{horizontal}"

    # --------------------------------------------------
    # PROCESS WEBCAM FRAME
    # --------------------------------------------------

    def process_frame(self, image_bytes):

        if self.landmarker is None:
            raise RuntimeError(
                "Start monitoring before sending frames."
            )

        encoded = np.frombuffer(
            image_bytes,
            dtype=np.uint8,
        )

        frame = cv2.imdecode(
            encoded,
            cv2.IMREAD_COLOR,
        )

        if frame is None:
            raise ValueError(
                "Invalid webcam image received."
            )

        # Mirror webcam image
        frame = cv2.flip(frame, 1)

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        timestamp_ms = max(
            int(time.monotonic() * 1000),
            self.last_timestamp_ms + 1,
        )

        self.last_timestamp_ms = timestamp_ms

        result = self.landmarker.detect_for_video(
            mp_image,
            timestamp_ms,
        )

        now = time.time()

        gaze = "NO FACE"
        face_detected = False

        horizontal_ratio = None
        vertical_ratio = None

        # --------------------------------------------------
        # FACE AND GAZE DETECTION
        # --------------------------------------------------

        if result.face_landmarks:

            face_detected = True
            landmarks = result.face_landmarks[0]

            (
                left_horizontal,
                left_vertical,
                left_horizontal_ratio,
                left_vertical_ratio,
            ) = self.estimate_gaze(
                landmarks,
                LEFT_EYE,
                LEFT_IRIS_CENTER,
                LEFT_EYE_VERTICAL,
            )

            (
                right_horizontal,
                right_vertical,
                right_horizontal_ratio,
                right_vertical_ratio,
            ) = self.estimate_gaze(
                landmarks,
                RIGHT_EYE,
                RIGHT_IRIS_CENTER,
                RIGHT_EYE_VERTICAL,
            )

            horizontal = self.combine_eye_estimates(
                left_horizontal,
                right_horizontal,
            )

            vertical = self.combine_eye_estimates(
                left_vertical,
                right_vertical,
            )

            gaze = self.combine_directions(
                horizontal,
                vertical,
            )

            # Average available debug ratios
            horizontal_values = [
                value for value in (
                    left_horizontal_ratio,
                    right_horizontal_ratio,
                )
                if value is not None
            ]

            vertical_values = [
                value for value in (
                    left_vertical_ratio,
                    right_vertical_ratio,
                )
                if value is not None
            ]

            if horizontal_values:
                horizontal_ratio = round(
                    sum(horizontal_values)
                    / len(horizontal_values),
                    3,
                )

            if vertical_values:
                vertical_ratio = round(
                    sum(vertical_values)
                    / len(vertical_values),
                    3,
                )

        # --------------------------------------------------
        # POSSIBLE DISTRACTION TRACKING
        # --------------------------------------------------

        distraction_seconds = 0.0
        message = "Gaze estimate: " + gaze

        if gaze in DISTRACTION_DIRECTIONS:

            if self.distraction_start is None:
                self.distraction_start = now
                self.event_saved = False

            distraction_seconds = (
                now - self.distraction_start
            )

            message = (
                f"Possible gaze deviation: {gaze}; "
                f"{distraction_seconds:.1f}s"
            )

            if (
                distraction_seconds >= DISTRACTION_SECONDS
                and not self.event_saved
            ):

                event = {
                    "event": "Possible Gaze Distraction",
                    "gaze": gaze,
                    "duration_seconds": round(
                        distraction_seconds, 2
                    ),
                    "timestamp": time.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }

                with self.lock:
                    self.events.append(event)

                self.event_saved = True

                message = (
                    "Possible gaze event recorded. "
                    "This is not proof of misconduct."
                )

        else:

            self.distraction_start = None
            self.event_saved = False

            if gaze == "NO FACE":
                message = (
                    "No face detected. Adjust your position."
                )

            elif gaze == "UNCERTAIN":
                message = (
                    "Eye estimates differ; result is uncertain."
                )

            elif gaze == "UNKNOWN":
                message = (
                    "Gaze could not be estimated reliably."
                )

            elif gaze == "CENTER":
                message = (
                    "Face detected. Gaze appears centered."
                )

            else:
                message = "Face detected. Gaze: " + gaze

        # --------------------------------------------------
        # UPDATE STATUS
        # --------------------------------------------------

        with self.lock:

            self.status = {
                "gaze": gaze,
                "face_detected": face_detected,
                "message": message,
                "distraction_seconds": round(
                    distraction_seconds, 1
                ),
                "event_count": len(self.events),
                "horizontal_ratio": horizontal_ratio,
                "vertical_ratio": vertical_ratio,
            }

            return dict(self.status)

    # --------------------------------------------------
    # GET CURRENT STATUS
    # --------------------------------------------------

    def get_status(self):

        with self.lock:
            return dict(self.status)

    # --------------------------------------------------
    # GET EVENTS
    # --------------------------------------------------

    def get_events(self):

        with self.lock:
            return [
                dict(event)
                for event in self.events
            ]

    # --------------------------------------------------
    # STOP MONITORING
    # --------------------------------------------------

    def stop(self):

        if self.landmarker is not None:
            self.landmarker.close()
            self.landmarker = None

        self.distraction_start = None
        self.event_saved = False

        with self.lock:
            self.status = {
                "gaze": "STOPPED",
                "face_detected": False,
                "message": "Monitoring stopped.",
                "distraction_seconds": 0.0,
                "event_count": len(self.events),
                "horizontal_ratio": None,
                "vertical_ratio": None,
            }


# ==================================================
# SHARED SERVICE INSTANCE
# ==================================================

gaze_service = GazeService()
