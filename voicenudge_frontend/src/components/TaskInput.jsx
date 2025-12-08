import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Mic, MicOff, Send, Upload, FileText } from 'lucide-react';
import api from '../api/client';
import toast from 'react-hot-toast';

const TaskInput = ({ onTaskAdded }) => {
  const [inputType, setInputType] = useState('text');
  const [textInput, setTextInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!textInput.trim()) {
      toast.error('📝 Please enter a task description');
      return;
    }

    setIsUploading(true);
    const loadingToast = toast.loading('✨ Processing your task...', {
      duration: Infinity,
    });
    
    try {
      await api.post('/api/tasks/ingest_text', { text: textInput });
      toast.dismiss(loadingToast);
      toast.success('🎯 Task added successfully! Ready to tackle it?', {
        duration: 4000,
      });
      setTextInput('');
      onTaskAdded();
    } catch (error) {
      toast.dismiss(loadingToast);
      toast.error('😞 Oops! Failed to add task. Please try again.', {
        duration: 5000,
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleVoiceUpload = async (audioBlob) => {
    setIsUploading(true);
    const loadingToast = toast.loading('🎤 Processing your voice input...', {
      duration: Infinity,
    });
    
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.webm');
      
      await api.post('/api/tasks/voice_ingest', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      toast.dismiss(loadingToast);
      toast.success('🎉 Voice task processed successfully! Your voice has been heard!', {
        duration: 4000,
      });
      onTaskAdded();
    } catch (error) {
      console.error('Voice upload error:', error);
      toast.dismiss(loadingToast);
      toast.error('🚨 Failed to process voice input. Please try recording again.', {
        duration: 5000,
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsUploading(true);
    const loadingToast = toast.loading('🎵 Processing your audio file...', {
      duration: Infinity,
    });
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      await api.post('/api/tasks/voice_ingest', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      toast.dismiss(loadingToast);
      toast.success('🎧 Audio file processed successfully! Ready to get things done!', {
        duration: 4000,
      });
      onTaskAdded();
    } catch (error) {
      console.error('File upload error:', error);
      toast.dismiss(loadingToast);
      toast.error('📁 Failed to process audio file. Please check the file format.', {
        duration: 5000,
      });
    } finally {
      setIsUploading(false);
    }
  };

  const startRecording = async () => {
    try {
      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        toast.error('🚫 Microphone access not supported in this browser');
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        handleVoiceUpload(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      toast.success('🎤 Microphone access granted! Start speaking...', {
        duration: 3000,
      });
    } catch (error) {
      console.error('Microphone error:', error);
      if (error.name === 'NotAllowedError') {
        toast.error('🔒 Microphone access denied. Please allow microphone access and try again.', {
          duration: 5000,
        });
      } else if (error.name === 'NotFoundError') {
        toast.error('🎙️ No microphone found. Please connect a microphone and try again.', {
          duration: 5000,
        });
      } else {
        toast.error('⚙️ Failed to access microphone. Please check your browser settings.', {
          duration: 5000,
        });
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
    >
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Add New Task</h3>
        
        
        {/* Input Type Toggle */}
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1 mb-4">
          <button
            onClick={() => setInputType('text')}
            className={`flex-1 flex items-center justify-center space-x-2 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              inputType === 'text'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
            }`}
          >
            <FileText className="h-4 w-4" />
            <span>Text</span>
          </button>
          <button
            onClick={() => setInputType('voice')}
            className={`flex-1 flex items-center justify-center space-x-2 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
              inputType === 'voice'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-200'
            }`}
          >
            <Mic className="h-4 w-4" />
            <span>Voice</span>
          </button>
        </div>
      </div>

      {/* Text Input */}
      {inputType === 'text' && (
        <form onSubmit={handleTextSubmit} className="space-y-4">
          <div>
            <label htmlFor="task-text" className="block text-sm font-medium text-gray-700 mb-2">
              Describe your task
            </label>
            <textarea
              id="task-text"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="e.g., Buy groceries, Call mom, Finish project report..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              rows={3}
              disabled={isUploading}
            />
          </div>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={!textInput.trim() || isUploading}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUploading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <Send className="h-4 w-4" />
            )}
            <span>{isUploading ? 'Processing...' : 'Add Task'}</span>
          </motion.button>
        </form>
      )}

      {/* Voice Input */}
      {inputType === 'voice' && (
        <div className="space-y-4">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-4">
              Record your task or upload an audio file
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {/* Record Button */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={isRecording ? stopRecording : startRecording}
                disabled={isUploading}
                className={`flex items-center justify-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                  isRecording
                    ? 'bg-red-600 text-white hover:bg-red-700 animate-pulse'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {isRecording ? (
                  <>
                    <MicOff className="h-5 w-5 animate-pulse" />
                    <span>Stop Recording</span>
                  </>
                ) : (
                  <>
                    <Mic className="h-5 w-5" />
                    <span>🎤 Start Recording</span>
                  </>
                )}
              </motion.button>

              {/* Upload Button */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
                className="flex items-center justify-center space-x-2 px-6 py-3 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Upload className="h-5 w-5" />
                <span>Upload Audio</span>
              </motion.button>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="audio/*"
              onChange={handleFileUpload}
              className="hidden"
            />

            {isRecording && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-4 flex items-center justify-center space-x-2 text-red-600"
              >
                <div className="animate-pulse w-2 h-2 bg-red-600 rounded-full"></div>
                <span className="text-sm font-medium">🎤 Recording... Speak now!</span>
              </motion.div>
            )}

            {isUploading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-4 flex items-center justify-center space-x-2 text-blue-600"
              >
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span className="text-sm font-medium">Processing...</span>
              </motion.div>
            )}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default TaskInput;
