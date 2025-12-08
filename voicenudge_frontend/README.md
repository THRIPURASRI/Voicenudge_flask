# VoiceNudge Frontend

A modern React.js frontend for the VoiceNudge AI Task Manager application.

## 🚀 Features

- **User Authentication**: Registration, login, and session management
- **Task Management**: Create, view, complete, and manage tasks
- **Voice Input**: Record voice notes or upload audio files for task creation
- **Text Input**: Quick text-based task creation
- **Task Dashboard**: View all tasks with filtering and statistics
- **User Profile**: View and manage user information
- **Activity History**: Track all task-related activities
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 🛠 Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and development server
- **React Router DOM** - Client-side routing
- **Axios** - HTTP client for API requests
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **React Hot Toast** - Toast notifications
- **Lucide React** - Beautiful icons

## 📁 Project Structure

```
voicenudge_frontend/
├── src/
│   ├── api/
│   │   └── client.js          # Axios API client configuration
│   ├── components/
│   │   ├── Navbar.jsx         # Navigation component
│   │   ├── TaskList.jsx       # Task display component
│   │   └── TaskInput.jsx      # Task creation component
│   ├── context/
│   │   └── AuthContext.jsx    # Authentication context
│   ├── pages/
│   │   ├── Login.jsx          # Login page
│   │   ├── Register.jsx       # Registration page
│   │   ├── Dashboard.jsx      # Main dashboard
│   │   ├── About.jsx         # User profile
│   │   └── History.jsx        # Activity history
│   ├── App.jsx                # Main app component with routing
│   ├── main.ts                # Application entry point
│   └── style.css              # Global styles with Tailwind
├── index.html                 # HTML template
├── package.json               # Dependencies and scripts
├── tailwind.config.js         # Tailwind configuration
└── vite.config.js            # Vite configuration
```

## 🚀 Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend API running on http://localhost:8888

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## 🔧 Configuration

### API Endpoint

The application is configured to connect to the backend API at `http://localhost:8888`. To change this, update the `baseURL` in `src/api/client.js`:

```javascript
const api = axios.create({
  baseURL: "http://your-backend-url:port",
  // ...
});
```

### Environment Variables

Create a `.env` file in the root directory to set environment variables:

```env
VITE_API_URL=http://localhost:8888
```

Then update the API client to use the environment variable:

```javascript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8888",
  // ...
});
```

## 📱 Pages and Features

### 🔐 Authentication
- **Login Page** (`/login`): Email and password authentication
- **Register Page** (`/register`): User registration with profile image upload
- **Auto-redirect**: Authenticated users are redirected to dashboard

### 📊 Dashboard (`/dashboard`)
- **Task Statistics**: Total, pending, completed, and overdue task counts
- **Task List**: View all tasks with filtering options
- **Task Creation**: Text input and voice recording for new tasks
- **Task Actions**: Mark complete, set due dates

### 👤 About Page (`/about`)
- **User Profile**: Display user information and profile image
- **Account Statistics**: Task completion metrics
- **Profile Editing**: Update user information (coming soon)

### 📜 History Page (`/history`)
- **Activity Log**: Track all task-related activities
- **Statistics**: Activity summaries and counts
- **Clear History**: Option to clear all activity history

## 🎨 UI/UX Features

- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Smooth Animations**: Framer Motion for page transitions and interactions
- **Toast Notifications**: Real-time feedback for user actions
- **Loading States**: Spinners and skeleton screens
- **Error Handling**: Graceful error messages and fallbacks

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Protected Routes**: Automatic redirects for unauthenticated users
- **Token Management**: Automatic token refresh and logout on expiry
- **Input Validation**: Client-side form validation

## 🚀 Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Netlify

1. Build the project: `npm run build`
2. Upload the `dist` folder to Netlify
3. Configure redirects for SPA routing

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Happy Task Managing! 🎯**
