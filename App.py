
from flask import Flask, render_template, request, jsonify, send_file
from gaze_service import gaze_service
import csv
import os
import threading
import webbrowser
import re

app = Flask(__name__)

# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REPORT_DIR = os.path.join(BASE_DIR, "reports")
REPORT_FILE = os.path.join(REPORT_DIR, "gaze_events.csv")

os.makedirs(REPORT_DIR, exist_ok=True)

APP_URL = "http://127.0.0.1:5000"


# --------------------------------------------------
# Candidate input validation
# --------------------------------------------------

def validate_candidate_details(candidate_name, candidate_id, role):

    # Candidate Name: English letters and spaces only
    if not re.fullmatch(r"[A-Za-z ]+", candidate_name):
        return "Candidate Name must contain only English letters and spaces."

    # Candidate ID: digits only
    if not re.fullmatch(r"[0-9]+", candidate_id):
        return "Candidate ID must contain numbers only."

    # Interview Role: English letters and spaces only
    if not re.fullmatch(r"[A-Za-z ]+", role):
        return "Interview Role must contain only English letters and spaces."

    return None


# --------------------------------------------------
# Home page
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# Candidate interview page
# --------------------------------------------------

@app.route("/interview", methods=["POST"])
def interview():
    candidate_name = request.form.get("name", "").strip()
    candidate_id = request.form.get("candidateId", "").strip()
    role = request.form.get("role", "").strip()

    # Check that all fields are filled
    if not candidate_name or not candidate_id or not role:
        return "Please fill in all candidate details.", 400

    # Validate all candidate details on the server
    validation_error = validate_candidate_details(
        candidate_name,
        candidate_id,
        role
    )

    if validation_error:
        return validation_error, 400

    return render_template(
        "interview.html",
        candidate_name=candidate_name,
        candidate_id=candidate_id,
        role=role
    )


# --------------------------------------------------
# Start gaze monitoring
# --------------------------------------------------

@app.route("/api/monitoring/start", methods=["POST"])
def start_monitoring():
    try:
        gaze_service.start()

        return jsonify({
            "success": True,
            "message": "Gaze monitoring started."
        })

    except Exception:
        app.logger.exception("Could not start gaze monitoring")

        return jsonify({
            "success": False,
            "message": (
                "Could not start monitoring. "
                "Check the Flask terminal."
            )
        }), 500


# --------------------------------------------------
# Process webcam frame
# --------------------------------------------------

@app.route("/api/monitoring/frame", methods=["POST"])
def process_frame():
    if gaze_service.landmarker is None:
        return jsonify({
            "success": False,
            "message": "Start monitoring first."
        }), 400

    image_file = request.files.get("frame")

    if image_file is None:
        return jsonify({
            "success": False,
            "message": "No webcam frame received."
        }), 400

    try:
        image_bytes = image_file.read()

        status = gaze_service.process_frame(image_bytes)

        return jsonify({
            "success": True,
            "status": status
        })

    except Exception:
        app.logger.exception("Frame processing failed")

        return jsonify({
            "success": False,
            "message": "Could not process webcam frame."
        }), 500


# --------------------------------------------------
# Get current monitoring status
# --------------------------------------------------

@app.route("/api/monitoring/status", methods=["GET"])
def monitoring_status():
    return jsonify(gaze_service.get_status())


# --------------------------------------------------
# Get gaze events
# --------------------------------------------------

@app.route("/api/monitoring/events", methods=["GET"])
def monitoring_events():
    return jsonify(gaze_service.get_events())


# --------------------------------------------------
# Stop monitoring and save CSV report
# --------------------------------------------------

@app.route("/api/monitoring/stop", methods=["POST"])
def stop_monitoring():
    events = gaze_service.get_events()

    try:
        with open(
            REPORT_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            fieldnames = [
                "event",
                "gaze",
                "duration_seconds",
                "timestamp"
            ]

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(events)

        return jsonify({
            "success": True,
            "message": "Monitoring stopped. Report saved.",
            "report": "reports/gaze_events.csv"
        })

    except Exception:
        app.logger.exception("Could not save monitoring report")

        return jsonify({
            "success": False,
            "message": "Report saving failed."
        }), 500

    finally:
        gaze_service.stop()


# --------------------------------------------------
# Download CSV report
# --------------------------------------------------

@app.route("/download-report", methods=["GET"])
def download_report():
    if not os.path.isfile(REPORT_FILE):
        return (
            "Report abhi available nahi hai. "
            "Pehle monitoring stop karein.",
            404
        )

    return send_file(
        REPORT_FILE,
        as_attachment=True,
        download_name="AI_Interview_Guard_Report.csv",
        mimetype="text/csv"
    )


# --------------------------------------------------
# Run application and open browser automatically
# --------------------------------------------------

if __name__ == "__main__":
    try:
        # Open browser shortly after Flask starts
        threading.Timer(
            1.5,
            lambda: webbrowser.open(APP_URL)
        ).start()

        app.run(
            host="127.0.0.1",
            port=5000,
            debug=True,
            threaded=True,
            use_reloader=False
        )

    finally:
        gaze_service.stop()
