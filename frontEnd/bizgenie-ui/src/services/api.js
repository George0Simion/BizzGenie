import axios from 'axios';
import { MOCK_RESTAURANT_DATA } from '../data/mockData';

// Frontend-ul vorbeste doar cu Proxy-ul (5000)
const PROXY_URL = 'http://localhost:5000/api/chat';

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const BusinessService = {
  getBusinessData: async () => {
    await delay(500); 
    return MOCK_RESTAURANT_DATA;
  },

  sendMessage: async (message, contextData) => {
    try {
      // Trimitem mesajul simplu catre Proxy
      const response = await axios.post(PROXY_URL, {
        message: message
      });
      
      // Proxy-ul ne-a formatat deja raspunsul corect ({ text: "...", sender: "ai" })
      return response.data;

    } catch (error) {
      console.error("Eroare API:", error);
      throw error;
    }
  }
};