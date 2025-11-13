import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface QueryResponse {
  query: string;
  response_text: string;
  hospitals_found: number;
}

export interface HealthResponse {
  status: string;
  hospitals_indexed?: number;
}

export const sendVoiceQuery = async (audioBlob: Blob): Promise<{
  audioUrl: string;
  transcribedText: string;
  responseText: string;
  hospitalsFound: number;
}> => {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.wav');

  const response = await axios.post(`${API_BASE_URL}/voice`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    responseType: 'blob',
  });

  const transcribedText = response.headers['x-transcribed-text'] || '';
  const responseText = response.headers['x-response-text'] || '';
  const hospitalsFound = parseInt(response.headers['x-hospitals-found'] || '0');

  const audioUrl = URL.createObjectURL(response.data);

  return {
    audioUrl,
    transcribedText,
    responseText,
    hospitalsFound,
  };
};

export const checkHealth = async (): Promise<HealthResponse> => {
  const response = await axios.get<HealthResponse>(`${API_BASE_URL}/health`);
  return response.data;
};