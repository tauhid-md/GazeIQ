# GazeIQ
AI-Powered Interview Monitoring System using Python, Flask, OpenCV and MediaPipe.
# GazeIQ: AI-Powered Interview Monitoring System

## 📌 Project Overview

GazeIQ is an AI-powered interview monitoring system designed to monitor a candidate's gaze direction during an online interview using computer vision.

The project uses Python, Flask, OpenCV, and MediaPipe to process webcam frames and monitor gaze-related events.

A web-based interface allows candidates to enter their details and start the interview monitoring process. The system collects monitoring events and saves them in a CSV report that can be downloaded for further analysis.

The main goal of GazeIQ is to demonstrate how AI and computer vision technologies can be used to support interview monitoring.

---

## 🎯 Project Objectives

The main objectives of this project are:

- Develop an AI-powered interview monitoring system.
- Collect candidate details through a web interface.
- Validate candidate information before starting the interview.
- Capture webcam frames for gaze monitoring.
- Process webcam frames using computer vision.
- Detect and record gaze-related events.
- Track the duration of recorded events.
- Save monitoring results in a CSV report.
- Provide a simple and interactive web-based interface.
- Allow users to download the monitoring report.
- Integrate a Python backend with a web frontend.

---

## 🔄 Project Workflow

The complete project follows this workflow:

Candidate Details  
↓  
Web Interface  
↓  
Input Validation  
↓  
Flask Backend  
↓  
Start Gaze Monitoring  
↓  
Capture Webcam Frames  
↓  
OpenCV and MediaPipe Processing  
↓  
Gaze Event Collection  
↓  
Save Monitoring Data to CSV  
↓  
Download Monitoring Report

---

## 👤 Candidate Information

The system collects the following candidate details before starting the interview monitoring process:

### Candidate Name

The name of the candidate participating in the interview.

### Candidate ID

A unique identification value used to distinguish the candidate.

### Interview Role

The position for which the candidate is being interviewed.

These details are submitted through an HTML form and passed to the Flask backend.

---

## 🧹 Input Validation

Input validation helps ensure that the candidate provides the required information before proceeding.

The validation process can include:

- Checking that all required fields are completed.
- Validating the candidate's name.
- Validating the candidate ID.
- Validating the interview role.
- Displaying appropriate error messages for invalid input.

Frontend validation improves the user experience, while backend validation provides an additional layer of checking.

---

## 👁️ AI and Computer Vision

GazeIQ uses computer vision libraries to process webcam frames and support gaze monitoring.

### OpenCV

OpenCV is a computer vision library used for image processing and computer vision tasks.

In this project, OpenCV is imported as `cv2` and is part of the gaze-monitoring implementation.

### MediaPipe

MediaPipe provides tools for processing visual information and detecting landmarks in images and video.

It is imported as `mediapipe` and aliased as `mp` in the gaze service.

The exact gaze-detection logic depends on the implementation in `gaze_service.py`.

**Note:** Gaze monitoring does not automatically prove that a candidate is cheating or behaving dishonestly. Gaze-related events should be interpreted as monitoring signals rather than definitive evidence of misconduct.

---

## 🎥 Webcam Frame Processing

The application includes a backend endpoint for receiving webcam frames.

The monitoring process follows these steps:

1. Start the gaze-monitoring service.
2. Receive webcam frames from the frontend.
3. Send the frames to the backend.
4. Process the received frames through the gaze service.
5. Return the processing status to the frontend.
6. Collect gaze-related events during monitoring.

The Flask backend provides API endpoints for starting monitoring, processing frames, checking status, retrieving events, and stopping monitoring.

---

## 📊 Gaze Event Monitoring

The system retrieves monitoring events from the gaze service.

The monitoring data is designed to record information such as:

- Event
- Gaze
- Duration in seconds
- Timestamp

These fields help organize the monitoring results and provide a record of the events collected during an interview session.

The actual event types and gaze-detection rules depend on the implementation of the gaze service.

---

## 💾 Report Generation and Data Storage

GazeIQ stores its monitoring report in CSV format.

### Report File

`reports/gaze_events.csv`

### Report Columns

- `event`
- `gaze`
- `duration_seconds`
- `timestamp`

The Python `csv` module is used to write the monitoring events into a CSV file.

The report is saved when the monitoring process is stopped through the application's stop-monitoring endpoint.

### Report Download

The application provides a download route:

`/download-report`

Users can download the generated CSV report for further analysis.

The report is stored locally in the project's `reports` directory. The current implementation does not require a database for this CSV-reporting workflow.

---

## 🌐 Web Application

GazeIQ uses Flask to connect the frontend with the Python backend.

The web application provides the following functionality:

- Display the candidate details form.
- Submit candidate information.
- Open the interview page.
- Start gaze monitoring.
- Send webcam frames to the backend.
- Retrieve monitoring status and events.
- Stop monitoring and save the report.
- Download the monitoring report.

The frontend is built using HTML, CSS, and JavaScript, while Flask manages application routes and backend processing.

---

## 🔌 Backend API Endpoints

The application defines the following Flask routes:

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Display the home page |
| `/interview` | POST | Validate candidate details and open the interview page |
| `/api/monitoring/start` | POST | Start gaze monitoring |
| `/api/monitoring/frame` | POST | Receive and process a webcam frame |
| `/api/monitoring/status` | GET | Retrieve monitoring status |
| `/api/monitoring/events` | GET | Retrieve collected events |
| `/api/monitoring/stop` | POST | Save the report and stop monitoring |
| `/download-report` | GET | Download the CSV report |

---

## 🛠️ Technologies Used

### Programming Language

- Python

### Frontend Development

- HTML5
- CSS3
- JavaScript

### Backend Development

- Flask
- Python standard library
- Flask routing and JSON APIs

### AI and Computer Vision

- OpenCV
- MediaPipe

### Data Storage and Reporting

- CSV
- Python `csv` module
- Local file storage

### Development Tools

- Visual Studio Code
- Python
- pip
- PowerShell / Terminal
- Web Browser
- Git
- GitHub

---

## 📁 Project Structure

The project structure is organized as follows:

```text
GazeIQ/
│
├── App.py
│
├── gaze_service.py
│
├── templates/
│   ├── index.html
│   └── interview.html
│
├── reports/
│   └── gaze_events.csv
│
├── README.md
│
└── requirements.txt
```

**Note:** The report file may be generated when monitoring is stopped. The `requirements.txt` file should contain the actual Python dependencies required by your project.

---

## ⚙️ How to Run the Project

### Step 1: Clone the Repository

Replace `YOUR_USERNAME` with your GitHub username.

```bash
git clone https://github.com/YOUR_USERNAME/GazeIQ.git
```

### Step 2: Open the Project Folder

```bash
cd GazeIQ
```

### Step 3: Create a Virtual Environment (Recommended)

```bash
python -m venv .venv
```

### Step 4: Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

For Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### Step 5: Install Required Libraries

```bash
pip install -r requirements.txt
```

Make sure the file contains the dependencies required by your actual code, including Flask, OpenCV, and MediaPipe, along with any additional dependencies used by `gaze_service.py`.

### Step 6: Run the Application

```bash
python App.py
```

The Flask application will start on:

`http://127.0.0.1:5000`

The application is configured to open the website in your default browser automatically.

### Step 7: Use the Application

1. Open the home page.
2. Enter the candidate's name, ID, and interview role.
3. Submit the candidate details.
4. Follow the interview page instructions to start monitoring.
5. Allow webcam access if requested by the browser.
6. Stop monitoring when finished.
7. Download the generated CSV report.

**Important:** Webcam access, camera permissions, and the installed MediaPipe dependencies must work correctly for monitoring to function.

---

## 📦 Required Libraries

The primary dependencies include:

```text
Flask
opencv-python
mediapipe
```

The project also uses Python standard-library modules such as:

- `csv`
- `os`
- `threading`
- `webbrowser`
- `re` (if backend regular-expression validation is enabled)

Create or update `requirements.txt` based on the libraries and versions that work with your current project environment.

---

## 🔐 Privacy and Limitations

GazeIQ is a prototype project for demonstrating computer vision-based interview monitoring.

- Webcam access requires the user's permission.
- Camera frames are processed by the application's backend.
- The current reporting implementation saves event data in a local CSV file.
- The project should not be treated as a fully reliable cheating-detection system.
- Gaze direction alone cannot determine a candidate's honesty, attention, or intentions.
- The application should be tested across different lighting conditions, camera positions, and users.
- Additional privacy safeguards are recommended before using the system in real interviews.

---

## 📚 Key Learning Outcomes

Through this project, I learned about:

- Building a web application using Flask.
- Connecting HTML forms with a Python backend.
- Validating user input.
- Creating Flask routes and REST-style API endpoints.
- Working with webcam-based image processing.
- Exploring OpenCV and MediaPipe.
- Sending image frames from a frontend to a backend.
- Handling JSON responses.
- Managing application errors.
- Recording monitoring events in CSV format.
- Generating downloadable reports.
- Organizing a Python project into separate modules.
- Managing project dependencies.
- Uploading and maintaining projects on GitHub.

---

## 🚀 Future Improvements

Possible future improvements include:

- Improve gaze-detection reliability.
- Add a real-time gaze status dashboard.
- Display monitoring events on the interview page.
- Add session summaries and visual reports.
- Generate PDF reports.
- Add candidate session history.
- Integrate a database for structured record management.
- Add authentication and role-based access.
- Improve the user interface and accessibility.
- Add configurable monitoring settings.
- Test performance under different lighting and camera conditions.
- Deploy the application to a secure hosting platform.
- Introduce stronger privacy controls and data-retention policies.

---

## 👨‍💻 Author

**Mohammad Tauhid Alam**

BSc.IT | AI/ML Student

Interested in:

- Artificial Intelligence
- Machine Learning
- Computer Vision
- Generative AI
- Python
- AI Projects

---

## ⭐ Support

If you find this project useful or interesting, consider giving the repository a star on GitHub.

Thank you for visiting **GazeIQ: AI-Powered Interview Monitoring System**!
