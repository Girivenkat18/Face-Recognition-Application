# Student Face Attendance System

An AI-powered attendance system that automates student attendance using real-time face recognition. Built with **Python**, **OpenCV**, and **Firebase**, this project captures, detects, and recognizes student faces to mark attendance efficiently and securely.

---

## Features

-  Real-time face detection and recognition using OpenCV
-  Firebase integration for cloud storage and database
-  Attendance marked automatically based on recognized faces
-  Attendance logs maintained with timestamps
-  Face registration functionality for new students
-  GUI interface for admin and student operations

---

## Tech Stack

- **Python 3**
- **OpenCV**
- **Face Recognition (dlib-based)**
- **Firebase Realtime Database & Storage**
- **Tkinter (for GUI)**

---

## Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Girivenkat18/student-face-attendance-system.git
   cd student-face-attendance-system
   ```

2. **Install Dependencies:**
   Required packages include:
   
    opencv-python
   
    face-recognition
   
    firebase-admin
   
    Pillow
   
    python-dotenv
   
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Firebase:**

   Create a Firebase project at firebase.google.com.
   
   Set up Realtime Database and Storage.
   
   Download the serviceAccountKey.json file and place it in your project folder.
   
   Update Firebase credentials in firebase_config.py.
   

6. **Run the Application:**
   ```bash
   python main.py
   ```
