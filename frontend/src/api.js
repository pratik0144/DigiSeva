import axios from 'axios';

const API_BASE_URL = 'http://localhost:5005';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const checkHealth = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

export const onboardUser = async (profileData) => {
  try {
    const response = await apiClient.post('/onboard', profileData);
    return response.data;
  } catch (error) {
    console.error('Onboarding failed:', error);
    throw error;
  }
};

export const sendChatMessage = async (accountId, message) => {
  try {
    const response = await apiClient.post('/chat', {
      account_id: accountId,
      message,
    });
    return response.data;
  } catch (error) {
    console.error('Chat failed:', error);
    throw error;
  }
};

export const resetSession = async (accountId) => {
  try {
    const response = await apiClient.post('/reset', {
      account_id: accountId,
    });
    return response.data;
  } catch (error) {
    console.error('Reset failed:', error);
    throw error;
  }
};

export const transcribeAudio = async (audioBlob, hintLanguage = null) => {
  try {
    const formData = new FormData();
    // Use an arbitrary filename
    formData.append('audio', audioBlob, 'voice_input.webm');
    
    if (hintLanguage) {
      formData.append('hint_language', hintLanguage);
    }

    const response = await axios.post(`${API_BASE_URL}/stt`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('STT failed:', error);
    throw error;
  }
};

export const generateSpeech = async (text, lang = 'hi') => {
  try {
    const response = await apiClient.post('/tts', 
      { text, lang },
      { responseType: 'blob' } // Important for audio files
    );
    return response.data;
  } catch (error) {
    console.error('TTS failed:', error);
    throw error;
  }
};
