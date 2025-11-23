import axios from 'axios';
import { MOCK_RESTAURANT_DATA } from '../data/mockData';

// URL-ul Proxy-ului (Middleman)
// Prioritizează VITE_PROXY_URL, altfel fallback explicit la localhost:5000/api
const PROXY_URL = (
  import.meta.env?.VITE_PROXY_URL ||
  'http://localhost:5000/api'
).replace(/\/+$/, '');

const api = axios.create({
  baseURL: PROXY_URL,
  timeout: 8000,
});

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const BusinessService = {
  // 1. Date simulate pentru Dashboard (la încărcare)
  getBusinessData: async () => {
    await delay(500); 
    return MOCK_RESTAURANT_DATA;
  },

  // 2. Trimitere mesaj CHAT (Frontend -> Proxy -> Target)
  sendMessage: async (message, contextData) => {
    try {
      // Trimitem la ruta /chat a proxy-ului
      const response = await api.post(`/chat`, {
        message: message,
        context: contextData
      });
      return response.data;
    } catch (error) {
      console.error("Chat error:", error);
      throw error;
    }
  },

  // 3. VERIFICARE ACTUALIZĂRI (Polling) - ASTA LIPSEA!
  checkUpdates: async () => {
    try {
      // Cerem noutățile de la Proxy
      const response = await api.get(`/updates`);
      
      // Proxy-ul returnează { updates: [...] }
      // Trebuie să returnăm array-ul, sau array gol dacă nu e nimic
      return response.data.updates || [];
    } catch (error) {
      // Dacă e eroare, nu blocăm aplicația, doar zicem că nu sunt update-uri
      // (e normal să dea eroare dacă proxy-ul e oprit)
      console.error("Polling error (verifică dacă Proxy.py rulează):", error.message);
      return [];
    }
  }

  // 4. Salvare task-uri legale (stub/no-op)
  ,
  saveLegalTasks: async (tasks) => {
    // Momentan nu avem un backend dedicat; returnăm resolved promise.
    console.log("saveLegalTasks (stub) called with", tasks?.length, "tasks");
    return true;
  }
};
