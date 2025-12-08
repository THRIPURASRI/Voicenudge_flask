import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, Lock, UserPlus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import VoiceRecorder from '../components/VoiceRecorder';
import api from '../api/client';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [voiceFile, setVoiceFile] = useState(null);
  const [showSecuritySection, setShowSecuritySection] = useState(false);
  const [securityQuestion, setSecurityQuestion] = useState("");
  const [securityAnswer, setSecurityAnswer] = useState("");
  const { login, isAuthenticated, updateUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  // Always try to fetch the registered security question once an email is present
  useEffect(() => {
    const loadQuestion = async () => {
      const email = formData.email?.trim();
      if (!email || !email.includes('@')) return;
      try {
        const resp = await api.get('/api/auth/security_question', {
          params: { email },
          validateStatus: (s) => s === 200 || s === 404,
        });
        if (resp.status === 200) {
          setSecurityQuestion(resp.data?.security_question || '');
        }
      } catch (e) {
        // ignore fetch errors, do not disturb login flow
      }
    };
    loadQuestion();
  }, [formData.email]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (!voiceFile) {
        toast('Please provide your voice for authentication.', { duration: 3000 });
      }
      const fd = new FormData();
      fd.append('email', formData.email);
      fd.append('password', formData.password);
      if (voiceFile) fd.append('voice', voiceFile);

      const resp = await api.post('/api/auth/login', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
        validateStatus: (s) => s === 200 || s === 206 || s === 403 || s === 401,
      });

      if (resp.status === 200) {
        const successMsg = resp?.data?.message || '🎉 Welcome back! Ready to tackle your tasks?';
        toast.success(successMsg, { duration: 4000 });
        try { await updateUser(); } catch (_) {}
        navigate('/dashboard');
      } else if (resp.status === 206) {
        if (resp.data?.security_question) {
          setSecurityQuestion(resp.data.security_question);
          setShowSecuritySection(true);
          toast('⚠️ Voice not verified. Please answer your security question.');
          return;
        }
      } else if (resp.status === 403) {
        toast.error('🔒 Account locked due to voice mismatch.');
      } else {
        toast.error(resp.data?.message || 'Login failed');
      }
    } catch (error) {
      toast.error('🚨 Login failed. Please check your credentials and try again.', {
        duration: 5000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifySecurity = async () => {
    if (!securityAnswer.trim()) {
      toast.error('Please enter your security answer.');
      return;
    }
    setIsLoading(true);
    try {
      const resp = await api.post('/api/auth/verify_security', {
        email: formData.email,
        answer: securityAnswer,
      }, {
        validateStatus: (s) => s === 200 || s === 401,
      });
      if (resp.status === 200) {
        toast.success(resp.data?.message || '✅ Security answer verified.');
        try { await updateUser(); } catch (_) {}
        navigate('/dashboard');
      } else {
        toast.error('❌ Incorrect answer.');
      }
    } catch (e) {
      toast.error('❌ Verification failed.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="sm:mx-auto sm:w-full sm:max-w-md"
      >
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2 }}
            className="mx-auto h-12 w-12 bg-blue-600 rounded-full flex items-center justify-center"
          >
            <UserPlus className="h-6 w-6 text-white" />
          </motion.div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">Welcome Back</h2>
          <p className="mt-2 text-sm text-gray-600">
            Sign in to your VoiceNudge account
          </p>
        </div>

        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email Address
              </label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your email"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="mt-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your password"
                />
              </div>
            </div>

            {/* Submit Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
              <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Signing in...</span>
                </div>
              ) : (
                'Sign In'
              )}
            </motion.button>
          </form>

          {/* Voice Recorder and Upload */}
          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Voice Verification</label>
            <VoiceRecorder onRecord={setVoiceFile} />
            {voiceFile && (
              <p className="mt-2 text-xs text-gray-500">Selected: {voiceFile.name}</p>
            )}
          </div>

          {/* Security Question Section (always visible) */}
          <div className="mt-6">
            <div className="border-t pt-4">
              <h3 className="text-md font-semibold text-red-600 mb-2">
                If voice not verified — answer the security question
              </h3>
              {securityQuestion ? (
                <p className="text-gray-700 mb-2">{securityQuestion}</p>
              ) : null}
              <input
                type="text"
                value={securityAnswer}
                onChange={(e) => setSecurityAnswer(e.target.value)}
                placeholder="Enter your answer"
                className="block w-full border rounded-md p-2 mb-3"
              />
              <button
                type="button"
                onClick={handleVerifySecurity}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                disabled={isLoading}
              >
                Verify Answer
              </button>
            </div>
          </div>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">New to VoiceNudge?</span>
              </div>
            </div>

            <div className="mt-6 text-center">
              <Link
                to="/register"
                className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                Create New Account
              </Link>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
