# 🎯 VoiceNudge User Flow Guide

This guide walks you through the complete user journey in the VoiceNudge application, following your desired flow.

## 🚀 Getting Started

1. **Start the Application:**
   ```bash
   cd voicenudge_frontend
   npm run dev
   ```
2. **Open Browser:** Navigate to `http://localhost:5173`
3. **Ensure Backend:** Make sure your Flask backend is running on `http://localhost:8888`

---

## 📋 Complete User Flow

### 1. 🔐 **Registration**
- **URL:** `/register`
- **Features:**
  - Full name input
  - Email address
  - Password creation
  - Confirm password
  - Profile image upload (optional)
- **Action:** Click "Create Account"
- **Result:** Redirects to Login page on success

### 2. 🔑 **Login**
- **URL:** `/login`
- **Features:**
  - Email and password fields
  - "Create New Account" link for new users
- **Action:** Click "Sign In"
- **Result:** Redirects to Dashboard on success

### 3. 🏠 **Dashboard (Main Interface)**
- **URL:** `/dashboard`
- **Features:**
  - Welcome message with user's name
  - Task statistics (Total, Pending, Completed, Overdue)
  - "Add Task" button to create new tasks
  - Task filtering (All, Pending, Completed, Overdue)
  - Task list with actions

### 4. ➕ **Task Creation (Text & Voice)**
- **Text Input:**
  - Click "Add Task" → Select "Text" tab
  - Type task description in textarea
  - Click "Add Task" button
- **Voice Input:**
  - Click "Add Task" → Select "Voice" tab
  - **Option A:** Click "Start Recording" → Speak → "Stop Recording"
  - **Option B:** Click "Upload Audio" → Select audio file
- **Result:** Task appears in dashboard list

### 5. 📋 **Task Management**
- **View Tasks:** All tasks displayed in cards with:
  - Title, description, category, priority
  - Due date, creation date, status
  - Action buttons
- **Set Due Date:**
  - Click "Set Due" button on any task
  - Enter date in YYYY-MM-DD format
  - Task updates with new due date
- **Complete Task:**
  - Click "Complete" button on any task
  - Task status changes to "Completed"
  - Green checkmark appears

### 6. 👤 **About Myself**
- **URL:** `/about`
- **Features:**
  - User profile information
  - Profile image display
  - Account statistics
  - Member since date
  - Edit profile option (coming soon)

### 7. 📜 **History**
- **URL:** `/history`
- **Features:**
  - Activity history with statistics
  - All task-related activities
  - Activity types: Task Created, Task Completed, Task Updated
  - Clear history button
- **Clear History:**
  - Click "Clear History" button
  - Confirm deletion
  - All history removed

### 8. 🚪 **Logout**
- **Method 1:** Click "Logout" in navbar
- **Method 2:** Click user menu → "Logout"
- **Result:** Redirects to Login page, clears session

---

## 🎨 **Navigation Flow**

```
Login/Register → Dashboard → About/History
     ↓              ↓
  Dashboard ← → Task Management
```

### **Navbar Links:**
- **Dashboard:** Main task management interface
- **About:** User profile and statistics
- **History:** Activity history
- **Logout:** Sign out and clear session

---

## 🔧 **Technical Features**

### **Authentication Flow:**
1. User registers → JWT token stored in localStorage
2. Token attached to all API requests
3. Auto-redirect to login if token invalid
4. Logout clears token and redirects

### **Task Management:**
1. **Text Ingestion:** POST to `/api/tasks/ingest_text`
2. **Voice Ingestion:** POST to `/api/tasks/voice_ingest`
3. **Set Due Date:** PATCH to `/api/tasks/<id>/set_due`
4. **Complete Task:** PATCH to `/api/tasks/<id>/complete`
5. **List Tasks:** GET from `/api/tasks/`

### **History Management:**
1. **View History:** GET from `/api/history/`
2. **Clear History:** DELETE to `/api/history/clear`

---

## 📱 **Responsive Design**

- **Desktop:** Full sidebar navigation
- **Tablet:** Collapsible navigation
- **Mobile:** Hamburger menu with slide-out navigation

---

## 🎯 **Key User Actions**

| Action | Page | Button/Input | API Endpoint |
|--------|------|--------------|--------------|
| Register | `/register` | Create Account | POST `/api/auth/register` |
| Login | `/login` | Sign In | POST `/api/auth/login` |
| Add Text Task | Dashboard | Add Task (Text) | POST `/api/tasks/ingest_text` |
| Add Voice Task | Dashboard | Add Task (Voice) | POST `/api/tasks/voice_ingest` |
| Set Due Date | Dashboard | Set Due | PATCH `/api/tasks/<id>/set_due` |
| Complete Task | Dashboard | Complete | PATCH `/api/tasks/<id>/complete` |
| View Profile | `/about` | Auto-loaded | GET `/api/auth/me` |
| View History | `/history` | Auto-loaded | GET `/api/history/` |
| Clear History | `/history` | Clear History | DELETE `/api/history/clear` |
| Logout | Any | Logout | POST `/api/auth/logout` |

---

## 🚀 **Quick Start Checklist**

- [ ] Backend running on `http://localhost:8888`
- [ ] Frontend running on `http://localhost:5173`
- [ ] Register new account
- [ ] Login with credentials
- [ ] Create tasks (text and voice)
- [ ] Set due dates
- [ ] Complete tasks
- [ ] View profile
- [ ] Check history
- [ ] Test logout

---

**🎉 Your VoiceNudge application is ready to use!**
