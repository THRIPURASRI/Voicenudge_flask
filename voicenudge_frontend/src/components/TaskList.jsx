import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Clock, Calendar, AlertCircle } from 'lucide-react';
import api from '../api/client';
import toast from 'react-hot-toast';

const TaskList = ({ tasks, onTaskUpdate }) => {
  const [loading, setLoading] = useState({});

  const handleComplete = async (taskId) => {
    const task = tasks.find(t => t.id === taskId);
    setLoading(prev => ({ ...prev, [taskId]: true }));
    
    // Show loading toast
    const loadingToast = toast.loading('🎯 Completing task...', {
      duration: Infinity,
    });
    
    try {
      await api.patch(`/api/tasks/${taskId}/complete`);
      toast.dismiss(loadingToast);
      toast.success(`🎉 Awesome! "${task?.title || 'Task'}" completed successfully!`, {
        duration: 4000,
      });
      onTaskUpdate();
    } catch (error) {
      toast.dismiss(loadingToast);
      toast.error(`😞 Oops! Failed to complete "${task?.title || 'task'}". Please try again.`, {
        duration: 5000,
      });
    } finally {
      setLoading(prev => ({ ...prev, [taskId]: false }));
    }
  };

  const handleSetDue = async (taskId) => {
    const task = tasks.find(t => t.id === taskId);
    
    // Enhanced date/time picker with better UX
    const date = window.prompt('📅 Pick date (YYYY-MM-DD):\nExample: 2024-12-25');
    if (!date) {
      toast.error('❌ Date selection cancelled');
      return;
    }
    
    const time = window.prompt('🕐 Pick time (HH:MM, 24h format):\nExample: 14:30');
    if (!time) {
      toast.error('❌ Time selection cancelled');
      return;
    }
    
    const dueDateIso = `${date}T${time}:00`;
    
    setLoading(prev => ({ ...prev, [taskId]: true }));
    
    // Show loading toast
    const loadingToast = toast.loading('⏰ Setting due date...', {
      duration: Infinity,
    });
    
    try {
      await api.patch(`/api/tasks/${taskId}/set_due`, { due_at: dueDateIso });
      toast.dismiss(loadingToast);
      toast.success(`📌 Perfect! Due date set for "${task?.title || 'task'}"`, {
        duration: 4000,
      });
      onTaskUpdate();
    } catch (error) {
      console.error('Set due date error:', error);
      toast.dismiss(loadingToast);
      toast.error(`🚨 Failed to set due date for "${task?.title || 'task'}"`, {
        duration: 5000,
      });
    } finally {
      setLoading(prev => ({ ...prev, [taskId]: false }));
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'text-red-600 bg-red-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100';
      case 'overdue':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No due date';
    // Normalize timestamps without timezone (assume UTC)
    let normalized = dateString;
    if (typeof dateString === 'string' && !dateString.includes('Z') && !/[+-]\d{2}:?\d{2}$/.test(dateString)) {
      normalized = dateString.replace(' ', 'T');
      if (!/T\d{2}:\d{2}:\d{2}Z?$/.test(normalized)) {
        // if seconds missing, append :00
        if (/T\d{2}:\d{2}$/.test(normalized)) normalized += ':00';
      }
      if (!normalized.endsWith('Z')) normalized += 'Z';
    }
    const date = new Date(normalized);
    if (Number.isNaN(date.getTime())) return 'Invalid date';
    // Render in the user's local timezone (real-world device time)
    const formatter = new Intl.DateTimeFormat(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
    return formatter.format(date);
  };

  if (!tasks || tasks.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center py-12"
      >
        <div className="text-gray-400 mb-4">
          <CheckCircle className="h-12 w-12 mx-auto" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks yet</h3>
        <p className="text-gray-500">Add your first task to get started!</p>
      </motion.div>
    );
  }

  return (
    <div className="space-y-4">
      {tasks.map((task, index) => (
        <motion.div
          key={task.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow ${task.status === 'completed' ? 'opacity-80' : ''}`}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <h3 className={`text-lg font-semibold text-gray-900 ${task.status === 'completed' ? 'line-through text-gray-500' : ''}`}>
                  {task.title}
                </h3>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(task.priority)}`}>
                  {task.priority || 'Normal'}
                </span>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(task.status)}`}>
                  {task.status || 'Pending'}
                </span>
              </div>
              
              {task.description && (
                <p className="text-gray-600 mb-3">{task.description}</p>
              )}
              
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                {task.category && (
                  <span className="flex items-center space-x-1">
                    <AlertCircle className="h-4 w-4" />
                    <span>{task.category}</span>
                  </span>
                )}
                {task.due_at && task.status !== 'completed' && (
                  <span className="flex items-center space-x-1">
                    <Calendar className="h-4 w-4" />
                  <span>Due: {formatDate(task.due_at)}</span>
                  </span>
                )}
                {/* created_at is not returned by /api/tasks; omit to prevent showing undefined */}
              </div>
            </div>
            
            <div className="flex items-center space-x-2 ml-4">
              {task.status !== 'completed' && (
                <>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleSetDue(task.id)}
                    disabled={loading[task.id]}
                    className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-md transition-colors disabled:opacity-50"
                  >
                    <Calendar className="h-4 w-4" />
                    <span>Set Due</span>
                  </motion.button>
                  
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleComplete(task.id)}
                    disabled={loading[task.id]}
                    className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-green-600 hover:text-green-700 hover:bg-green-50 rounded-md transition-colors disabled:opacity-50"
                  >
                    <CheckCircle className="h-4 w-4" />
                    <span>Complete</span>
                  </motion.button>
                </>
              )}
              
              {task.status === 'completed' && (
                <div className="flex items-center space-x-1 text-green-600">
                  <CheckCircle className="h-5 w-5" />
                  <span className="text-sm font-medium">Completed</span>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default TaskList;
