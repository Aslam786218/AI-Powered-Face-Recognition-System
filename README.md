# 🤖 AI-Powered Face Recognition Attendance System

An AI-powered face recognition system that automatically detects and identifies individuals using facial features. The system is designed for **attendance management**, providing a fast, contactless, and efficient solution.

---

## 🚀 Features

- 🎯 Face Detection & Recognition using AI
- 🧠 Liveness Detection (prevents fake/spoof attacks)
- 📸 Real-time camera-based recognition
- 🗂️ Stores known faces for identification
- 📊 Attendance marking system
- 🌐 Web interface (Login & Dashboard)
- 🧾 Easy integration with backend (Flask)

---

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS
- **Backend:** Python (Flask)
- **Libraries Used:**
  - OpenCV
  - face_recognition
  - NumPy
- **Others:**
  - Liveness Detection
  - Image Processing

---

## 📁 Project Structure

AI-Powered-Face-Recognition-System/


├── known_faces/               
    
    └── download.jpg


├── sample_images/ 
    
    └── download.jpg


├── templates/

    └── login.html
    
    └── dashboard.html



├── attendance_system.py

├── facerecognition_final.py 

├── liveness.py          

├── app.py                
├── README.md            
└── .gitignore

---

## ⚙️ How It Works

1. 📷 Capture image using webcam  
2. 🧠 Detect face using OpenCV  
3. 🔍 Extract facial features  
4. 🆔 Compare with stored faces  
5. ✅ If matched → mark attendance  
6. 🚫 If not matched → ignore  
7. 🛡️ Liveness detection ensures real person  

---

## 🧑‍💻 Installation & Setup

### 1️⃣ Clone the Repository

git clone https://github.com/Aslam786218/AI-Powered-Face-Recognition-System.git
cd AI-Powered-Face-Recognition-System

---

### 2️⃣ Install Dependencies

pip install opencv-python  
pip install face-recognition  
pip install numpy  
pip install flask  

---

### 3️⃣ Run the Application

python app.py

---

### 4️⃣ Open in Browser

http://127.0.0.1:5000/

---

## 📌 Usage

- Add images of users in **known_faces/**
- Run the system
- Login using web interface
- Start attendance tracking
- Dashboard will display attendance records

---

## 🔒 Liveness Detection

The system includes a **liveness detection module** (`liveness.py`) to prevent:

- Fake photos  
- Video spoofing  
- Unauthorized access  

---

## 📊 Future Improvements

- 📱 Mobile app integration  
- 🗄️ Database (MySQL/PostgreSQL)  
- ☁️ Cloud deployment  
- 🧾 Advanced attendance analytics  
- 🔐 Role-based authentication  

---

## 🤝 Contribution

Contributions are welcome!

1. Fork the repository  
2. Create a new branch  
3. Make your changes  
4. Submit a pull request  

---

## 📜 License

This project is for educational purposes.

---

## 👨‍💻 Author

Aslam Sayyad  
Email: as2478657@gmail.com  
LinkedIn: https://www.linkedin.com/in/aslam-sayyad-aa0559373  
GitHub: https://github.com/Aslam786218  

---

## ⭐ Support

If you like this project, give it a star on GitHub!
