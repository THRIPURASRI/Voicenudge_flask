import React, { useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';

const VoiceRecorder = ({ onRecord, allowUpload = true, maxMs = 20000 }) => {
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timeoutRef = useRef(null);
  const startTimeRef = useRef(0);
  const [isRecording, setIsRecording] = useState(false);
  const [hasMicPermission, setHasMicPermission] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');

  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setHasMicPermission(true);
      const mediaRecorder = new MediaRecorder(stream);
      chunksRef.current = [];
      mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };
      mediaRecorder.onstop = () => {
        const durationMs = Date.now() - startTimeRef.current;
        const blob = new Blob(chunksRef.current, { type: 'audio/wav' });
        const file = new File([blob], 'sample.wav', { type: 'audio/wav' });
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        const url = URL.createObjectURL(blob);
        setPreviewUrl(url);
        if (durationMs < 15000) {
          toast.error('Please record at least 15 seconds of voice for better accuracy.');
          // Do not emit the short recording; user should try again
        } else {
          onRecord && onRecord(file);
        }
        stream.getTracks().forEach((t) => t.stop());
      };
      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      startTimeRef.current = Date.now();
      timeoutRef.current = setTimeout(() => stopRecording(), maxMs);
    } catch (e) {
      setHasMicPermission(false);
      console.error('Microphone access denied or unavailable', e);
    }
  };

  const stopRecording = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== 'inactive') {
      recorder.stop();
    }
    setIsRecording(false);
  };

  const onUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    onRecord && onRecord(file);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        {!isRecording ? (
          <button
            type="button"
            onClick={startRecording}
            className="px-3 py-2 rounded-md bg-blue-600 text-white text-sm hover:bg-blue-700"
          >
            {hasMicPermission === false ? 'Mic blocked' : 'Record Voice'}
          </button>
        ) : (
          <button
            type="button"
            onClick={stopRecording}
            className="px-3 py-2 rounded-md bg-red-600 text-white text-sm hover:bg-red-700"
          >
            Stop
          </button>
        )}
        {allowUpload && (
          <label className="px-3 py-2 rounded-md border text-sm cursor-pointer bg-gray-50 hover:bg-gray-100">
            Upload .wav
            <input type="file" accept="audio/wav" onChange={onUpload} className="hidden" />
          </label>
        )}
      </div>
      {isRecording && (
        <p className="text-sm text-gray-600">🎙️ Recording… Speak naturally for 15–20 seconds.</p>
      )}
      {previewUrl && (
        <audio src={previewUrl} controls className="w-full" />
      )}
    </div>
  );
};

export default VoiceRecorder;


