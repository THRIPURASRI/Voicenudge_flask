# 🎙️ VoiceNudge — AI Powered Daily Task Manager (Flask + React + ML + Voice Authentication)

VoiceNudge is an intelligent, voice-driven task management system that allows users to **speak their tasks**, automatically categorizes them using **Machine Learning**, assigns **priority levels**, stores them securely, and triggers **smart reminders** using an automated scheduler.

The system also includes **voice authentication** using a pretrained ECAPA-VoxCeleb model to ensure that tasks are added only by the authenticated user.

---

## 🚀 Features

### 🔊 **1. Voice-Based Task Creation**
- Users speak their task.
- Whisper model converts speech → text.
- System extracts date/time, category, and intent.

### 🗣️ **2. Voice Authentication**
- Uses **ECAPA-VoxCeleb offline model (.ckpt)**.
- Embeddings compare user voice with stored profile.
- Prevents unauthorized access or fake task creation.

### 🤖 **3. Intelligent Task Classification**
ML model predicts:
- **Category:** Work, Health, Personal, Finance, Errands, etc.
- **Priority:** High, Medium, Low  
Dataset used: `datasets/tasks_dataset.csv`

### 🗂️ **4. Task Management System**
- Stores tasks in **PostgreSQL** using SQLAlchemy ORM.
- Exposes REST APIs for CRUD operations.
- Clean backend architecture (Blueprints).

### ⏰ **5. Smart Reminder Scheduler**
- APScheduler job runs every minute.
- Sends reminders when deadlines match.
- Designed for high reliability and future SMS/email integration.

### 💻 **6. Modern Frontend**
- React (Vite) UI
- Voice input button
- Task dashboard with filters
- Real-time updates via backend APIs

### 📦 **7. Git LFS Enabled for Large Files**
- ECAPA model stored using Git Large File Storage.
- Repository stays clean and lightweight.

---

## 🏗️ System Architecture

```
User Voice → Whisper STT → Flask Backend → ML Classifier
          → Voice Authentication → PostgreSQL → React UI
          → Reminder Scheduler → Notifications
```

---

## 📁 Project Structure

```
VoiceNudge-main/
│
├── voicenudge_backend/
│   ├── datasets/
│   │   └── tasks_dataset.csv
│   ├── pretrained_models/
│   │   └── ecapa_voxceleb_offline/embedding_model.ckpt
│   ├── voicenudge/
│   │   ├── routes/
│   │   ├── models/
│   │   ├── utils/
│   │   └── scheduler/
│   ├── migrations/
│   ├── tests/
│   ├── train/
│   └── app.py
│
└── voicenudge_frontend/
    ├── src/
    ├── components/
    ├── pages/
    └── main.jsx
```

---

## ⚙️ Installation & Setup

### **1️⃣ Clone the repository**
```bash
git clone https://github.com/THRIPURASRI/Voicenudge_flask.git
cd VoiceNudge-main
```

---

## 🛠️ Backend Setup (Flask)

### **2️⃣ Create virtual environment**
```bash
cd voicenudge_backend
python -m venv venv
venv/Scripts/activate      # Windows
```

### **3️⃣ Install dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Set up environment variables**
Create `.env` file:

```
DATABASE_URL=postgresql://username:password@localhost:5432/voicenudge
SECRET_KEY=your_secret_key
```

### **5️⃣ Initialize database**
```bash
flask db init
flask db migrate
flask db upgrade
```

### **6️⃣ Run backend**
```bash
flask run
```

---

## 🌐 Frontend Setup (React + Vite)

### **1️⃣ Install dependencies**
```bash
cd voicenudge_frontend
npm install
```

### **2️⃣ Run development server**
```bash
npm run dev
```

---

## 🔐 Voice Authentication

We use:

- **ECAPA-VoxCeleb embedding model**
- Stored using **Git LFS**
- Converts user voice → embedding → compares with stored profile

This ensures **secure, personalized task creation**.

---

## 🧠 Machine Learning Models

### **Task Classification**
- ML model trained on `tasks_dataset.csv`
- Predicts **category & priority**
- Can be retrained from `train/` folder

### **Speech to Text**
- Whisper model (small)

---

## ⏳ Reminder Scheduler

- APScheduler interval job runs every 60 seconds.
- Detects upcoming deadlines.
- Triggers reminders (email/notification).
- Fully integrated with SQLAlchemy models.

---

## 🧪 Testing

Backend tests located in:
```
voicenudge_backend/tests/
```

Run tests:
```bash
pytest
```

---

## 🐙 Git LFS Support

Large model files tracked using:

```bash
git lfs track "*.ckpt"
```

---

## 🤝 Contributing

Pull requests are welcome!  
Please open an issue to discuss major changes.

---

## 📄 License
MIT License (or add your license here)

---

## ✨ Author
**Thripurasri S**  
B.Tech (Information Science & Engineering)  
RV College of Engineering, Bengaluru

---

## ⭐ If you like this project…
Give it a ⭐ on GitHub!
