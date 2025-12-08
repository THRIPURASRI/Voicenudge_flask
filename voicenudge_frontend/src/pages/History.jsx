import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Trash2, RefreshCw, Calendar, Clock, AlertTriangle } from 'lucide-react';
import api from '../api/client';
import toast from 'react-hot-toast';

const History = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isClearing, setIsClearing] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/history/');
      const raw = response.data || [];
      // Normalize items: infer type and timestamp from backend fields
      const normalized = raw.map((item) => {
        const inferredType = (item.status === 'completed' || item.status === 'archived')
          ? 'task_completed'
          : 'task_updated';

        // Some backend timestamps are UTC but sent without timezone (e.g., "2025-10-05 17:31:00").
        // Treat such values as UTC and convert properly later when formatting.
        const rawTs = item.completed_at || item.due_at || item.created_at || item.timestamp || null;
        const timestamp = normalizeUtcString(rawTs);

        return {
          ...item,
          type: item.type || inferredType,
          timestamp,
        };
      });
      setHistory(normalized);
    } catch (error) {
      toast.error('Failed to fetch history');
    } finally {
      setLoading(false);
    }
  };

  const normalizeUtcString = (val) => {
    if (!val) return null;
    if (typeof val === 'string') {
      // If it already contains timezone info, return as-is
      if (val.includes('Z') || /[+-]\d{2}:?\d{2}$/.test(val)) {
        return val;
      }
      // No explicit TZ: treat as UTC. Accept either space-separated or already with 'T'
      const compact = val.trim();
      if (/^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}$/.test(compact)) {
        return compact.replace(' ', 'T') + 'Z';
      }
    }
    return val;
  };

  const handleClearHistory = async () => {
    if (!window.confirm('Are you sure you want to clear all history? This action cannot be undone.')) {
      return;
    }

    try {
      setIsClearing(true);
      await api.delete('/api/history/clear');
      setHistory([]);
      toast.success('History cleared successfully');
    } catch (error) {
      toast.error('Failed to clear history');
    } finally {
      setIsClearing(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    const formatter = new Intl.DateTimeFormat('en-IN', {
      timeZone: 'Asia/Kolkata',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
    return `${formatter.format(date)} IST`;
  };

  const getActivityIcon = (activity) => {
    switch (activity?.type?.toLowerCase()) {
      case 'task_created':
        return <Calendar className="h-5 w-5 text-blue-600" />;
      case 'task_completed':
        return <Clock className="h-5 w-5 text-green-600" />;
      case 'task_updated':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      default:
        return <Clock className="h-5 w-5 text-gray-600" />;
    }
  };

  const getActivityColor = (activity) => {
    switch (activity?.type?.toLowerCase()) {
      case 'task_created':
        return 'bg-blue-50 border-blue-200';
      case 'task_completed':
        return 'bg-green-50 border-green-200';
      case 'task_updated':
        return 'bg-yellow-50 border-yellow-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading history...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Activity History</h1>
              <p className="mt-2 text-gray-600">
                Track your task management activities
              </p>
            </div>
            
            <div className="mt-4 sm:mt-0 flex space-x-3">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={fetchHistory}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Refresh</span>
              </motion.button>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleClearHistory}
                disabled={isClearing || history.length === 0}
                className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Trash2 className="h-4 w-4" />
                <span>{isClearing ? 'Clearing...' : 'Clear History'}</span>
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Stats Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8"
        >
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span className="text-blue-600 font-semibold">{history.length}</span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Activities</p>
                <p className="text-2xl font-bold text-gray-900">{history.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                  <span className="text-green-600 font-semibold">
                    {history.filter(h => h.type === 'task_completed').length}
                  </span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Tasks Completed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {history.filter(h => h.type === 'task_completed').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <span className="text-yellow-600 font-semibold">
                    {history.filter(h => h.type === 'task_created').length}
                  </span>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Tasks Created</p>
                <p className="text-2xl font-bold text-gray-900">
                  {history.filter(h => h.type === 'task_created').length}
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* History List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          {history.length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
              <div className="text-gray-400 mb-4">
                <Clock className="h-12 w-12 mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No activity yet</h3>
              <p className="text-gray-500">Your task activities will appear here</p>
            </div>
          ) : (
            <div className="space-y-4">
              {history.map((activity, index) => (
                <motion.div
                  key={activity.id || index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`bg-white rounded-lg shadow-sm border p-6 ${getActivityColor(activity)}`}
                >
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      {getActivityIcon(activity)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {activity.title || 'Activity'}
                        </h3>
                        {/* Per request: hide time on history items */}
                      </div>
                      
                      {activity.description && (
                        <p className="mt-2 text-gray-600">{activity.description}</p>
                      )}
                      
                      <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
                        <span className="flex items-center space-x-1">
                          <span className="font-medium">Type:</span>
                          <span className="capitalize">{activity.type?.replace('_', ' ')}</span>
                        </span>
                        
                        {activity.task_id && (
                          <span className="flex items-center space-x-1">
                            <span className="font-medium">Task ID:</span>
                            <span>{activity.task_id}</span>
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default History;
