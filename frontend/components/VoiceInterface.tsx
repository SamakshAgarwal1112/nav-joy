'use client';

import { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Loader2, Volume2 } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  text: string;
  timestamp: Date;
}

export default function VoiceInterface() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    audioRef.current = new Audio();
    
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      setError(null);
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000,
        } 
      });

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
      });

      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: 'audio/webm' 
        });
        
        stream.getTracks().forEach(track => track.stop());
        
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      
    } catch (err) {
      console.error('Error accessing microphone:', err);
      setError('Failed to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleMicClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6">
      <div className="w-full max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-3">
            Loop AI
          </h1>
          <p className="text-xl text-gray-600">
            Voice-Powered Hospital Network Assistant
          </p>
        </div>

        <div className="flex flex-col items-center mb-12">
          <button
            onClick={handleMicClick}
            disabled={isProcessing}
            className={`
              relative w-32 h-32 rounded-full shadow-2xl transition-all duration-300
              flex items-center justify-center
              ${isRecording 
                ? 'bg-red-500 hover:bg-red-600 scale-110 animate-pulse' 
                : isProcessing
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 hover:scale-105'
              }
            `}
          >
            {isProcessing ? (
              <Loader2 className="w-16 h-16 text-white animate-spin" />
            ) : isRecording ? (
              <MicOff className="w-16 h-16 text-white" />
            ) : (
              <Mic className="w-16 h-16 text-white" />
            )}
            
            {isRecording && (
              <span className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 
                             bg-red-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                Recording...
              </span>
            )}
          </button>

          <p className="mt-6 text-gray-600 text-center max-w-md">
            {isRecording 
              ? 'Click again to stop recording'
              : isProcessing 
              ? 'Processing your query...'
              : 'Click the microphone to start speaking'}
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-center">
            {error}
          </div>
        )}

        {messages.length > 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-6 space-y-4 max-h-96 overflow-y-auto">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <Volume2 className="w-6 h-6" />
              Conversation
            </h2>
            
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`
                    max-w-[75%] rounded-2xl px-5 py-3 shadow-sm
                    ${message.role === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-100 text-gray-800'
                    }
                  `}
                >
                  <p className="text-sm font-medium mb-1 opacity-75">
                    {message.role === 'user' ? 'You' : 'Loop AI'}
                  </p>
                  <p className="whitespace-pre-wrap leading-relaxed">
                    {message.text}
                  </p>
                  <p className="text-xs mt-2 opacity-60">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}

        {messages.length === 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              Try asking:
            </h3>
            <ul className="space-y-3 text-gray-600">
              <li className="flex items-start gap-3">
                <span className="text-blue-600 font-bold">•</span>
                <span>"Tell me 3 hospitals around Bangalore"</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-blue-600 font-bold">•</span>
                <span>"Can you confirm if Manipal Sarjapur in Bangalore is in my network?"</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-blue-600 font-bold">•</span>
                <span>"Show me hospitals in Mumbai"</span>
              </li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}