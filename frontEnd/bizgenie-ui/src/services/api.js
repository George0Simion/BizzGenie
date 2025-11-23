import axios from 'axios';
import { MOCK_RESTAURANT_DATA } from '../data/mockData';

// URL-ul Proxy-ului
const PROXY_URL = 'http://localhost:5000/api';

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const BusinessService = {
  // 1. Date Dashboard
  getBusinessData: async () => {
    await delay(500); 
    return MOCK_RESTAURANT_DATA;
  },

  // 2. Chat
  sendMessage: async (message, contextData) => {
    const response = await axios.post(`${PROXY_URL}/chat`, { message, context: contextData });
    return response.data;
  },

  // 3. Polling
  checkUpdates: async () => {
    try {
      const response = await axios.get(`${PROXY_URL}/updates`);
      return response.data.updates || [];
    } catch (error) {
      return [];
    }
  },

  // 4. SAVE LEGAL (NOU)
  saveLegalTasks: async (tasks) => {
    try {
      // Trimitem lista modificata catre Proxy
      const response = await axios.post(`${PROXY_URL}/legal/save`, { tasks });
      return response.data;
    } catch (error) {
      console.error("Save error:", error);
      throw error;
    }
  }
};