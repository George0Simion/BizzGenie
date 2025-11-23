import React, { createContext, useState, useContext, useEffect } from 'react';
import { BusinessService } from '../services/api';
import { MOCK_RESTAURANT_DATA } from '../data/mockData';

const BusinessContext = createContext();

export const BusinessProvider = ({ children }) => {
  // ==========================================
  // 1. STATE-URI (MEMORIA APLICAȚIEI)
  // ==========================================
  
  // Date despre Business
  const [businessData, setBusinessData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Notificări
  const [notifications, setNotifications] = useState([]);
  const [isNotificationPanelOpen, setIsNotificationPanelOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  // Chat UI
  const [isChatOpen, setIsChatOpen] = useState(true);

  // Inventar
  const [inventoryItems, setInventoryItems] = useState(MOCK_RESTAURANT_DATA.inventory);

  // Legal (Checklist)
  const [legalTasks, setLegalTasks] = useState([]);

  // Mesaje Chat Global
  const [chatMessages, setChatMessages] = useState([
    { id: 1, text: "Salut! Sunt BizGenie. Monitorizez activitatea.", sender: 'ai' }
  ]);

  // Helper pentru adaugare mesaj in chat
  const addChatMessage = (text, sender = 'ai') => {
    setChatMessages(prev => [...prev, { 
      id: Date.now() + Math.random(), 
      text, 
      sender 
    }]);
  };


  // ==========================================
  // 2. INITIALIZARI & EFECTE
  // ==========================================

  // Initializare date mock la login
  useEffect(() => {
    if (businessData) {
      setNotifications(MOCK_RESTAURANT_DATA.urgent_actions.map(n => ({...n, read: false, time: 'Acum'})));
      
      // Initializam si Legal Tasks din mock data daca exista
      if (MOCK_RESTAURANT_DATA.legal && MOCK_RESTAURANT_DATA.legal.checklist) {
          setLegalTasks(MOCK_RESTAURANT_DATA.legal.checklist);
      }
    }
  }, [businessData]);

  // Calculare notificari necitite
  useEffect(() => {
    setUnreadCount(notifications.filter(n => !n.read).length);
  }, [notifications]);


  // --- POLLING SYSTEM (PRIMIRE DATE AUTOMATE DE LA SERVER) ---
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const updates = await BusinessService.checkUpdates();

        if (updates && updates.length > 0) {
          updates.forEach(packet => {

            // CAZ 1: Actualizare Inventar
            if (packet.type === 'data_update' && packet.payload.category === 'inventory') {
              // console.log("📦 [UI] Update Inventar:", packet.payload.items);
              setInventoryItems(packet.payload.items);
            }

            // CAZ 2: Actualizare Legal (NOU)
            if (packet.type === 'data_update' && packet.payload.category === 'legal') {
              console.log("⚖️ [UI] Update Legal primit de la server.");
              // Suprascriem datele locale cu cele de pe server
              setLegalTasks(packet.payload.tasks);
            }

            // CAZ 3: Mesaj Chat
            if (packet.type === 'chat_message') {
               addChatMessage(packet.payload.text, 'ai');
            }

            // CAZ 4: Notificări
            if (packet.type === 'notification') {
               setNotifications(prev => [{
                  id: Date.now() + Math.random(),
                  title: packet.payload.title,
                  desc: packet.payload.desc,
                  type: packet.payload.type || 'info',
                  time: 'Acum',
                  read: false,
                  agent: 'System'
               }, ...prev]);
            }
          });
        }
      } catch (e) {
        console.error("Polling error (verifică Proxy-ul)", e);
      }
    }, 2000); // Verificam la fiecare 2 secunde

    return () => clearInterval(interval);
  }, []);


  // ==========================================
  // 3. FUNCȚII (ACȚIUNI)
  // ==========================================

  const startNewBusiness = async (description) => {
    setIsLoading(true);
    setTimeout(() => {
      setBusinessData({ name: "Business Nou", type: "restaurant", stage: "startup", details: description });
      setIsLoading(false);
    }, 1500);
  };

  const connectExistingBusiness = async (formData) => {
    setIsLoading(true);
    setTimeout(() => {
      setBusinessData({ name: formData.name, type: "restaurant", cui: formData.cui, stage: "active" });
      setIsLoading(false);
    }, 1000);
  };

  // Notificari
  const toggleNotifications = () => setIsNotificationPanelOpen(prev => !prev);
  const markAsRead = (id) => setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  const markAllAsRead = () => setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  const deleteNotification = (id) => setNotifications(prev => prev.filter(n => n.id !== id));

  // Chat
  const toggleChat = () => setIsChatOpen(prev => !prev);
  const sendMessage = async (msg) => {
    return await BusinessService.sendMessage(msg, {});
  };

  // --- LOGICA LEGAL (NOU) ---
  
  // 1. Schimbă statusul unui pas (bifă)
  const toggleLegalStep = (taskId, stepName) => {
    setLegalTasks(prevTasks => prevTasks.map(task => {
      if (task.id !== taskId) return task;
      
      // Actualizam pasii
      const updatedSteps = task.steps.map(s => {
        if (s.step !== stepName) return s;
        return { ...s, done: !s.done };
      });

      // Calculam automat noul status
      const allDone = updatedSteps.every(s => s.done);
      const anyDone = updatedSteps.some(s => s.done);
      
      let newStatus = 'pending';
      if (allDone) {
          newStatus = 'completed';
      } else if (anyDone) {
          newStatus = 'in_progress';
      }

      return { ...task, steps: updatedSteps, status: newStatus };
    }));
  };

  // 2. Sterge un task local
  const deleteLegalTask = (taskId) => {
      setLegalTasks(prev => prev.filter(t => t.id !== taskId));
  };

  // 3. Trimite tot obiectul la server (SAVE)
  const saveLegalChanges = async () => {
      console.log("💾 UI: Se trimite salvarea Legal catre server...");
      try {
          await BusinessService.saveLegalTasks(legalTasks);
          addChatMessage("Am trimis actualizările legale către server.", "system");
      } catch (e) {
          console.error("Save failed", e);
          throw e; // Aruncam eroarea ca sa o prinda UI-ul (Legal.jsx)
      }
  };


  // ==========================================
  // 4. PROVIDER
  // ==========================================
  return (
    <BusinessContext.Provider value={{ 
      businessData, isLoading, startNewBusiness, connectExistingBusiness,
      notifications, unreadCount, isNotificationPanelOpen, toggleNotifications, markAsRead, markAllAsRead, deleteNotification,
      isChatOpen, toggleChat, chatMessages, addChatMessage, sendMessage,
      inventoryItems, setInventoryItems,
      
      // Exportam tot ce tine de LEGAL
      legalTasks, setLegalTasks, toggleLegalStep, deleteLegalTask, saveLegalChanges
    }}>
      {children}
    </BusinessContext.Provider>
  );
};

export const useBusiness = () => useContext(BusinessContext);