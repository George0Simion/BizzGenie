import React, { createContext, useState, useContext, useEffect } from 'react';
import { MOCK_RESTAURANT_DATA } from '../data/mockData';

const BusinessContext = createContext();

export const BusinessProvider = ({ children }) => {
  const [businessData, setBusinessData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // --- LOGICA DE NOTIFICĂRI ---
  const [isNotificationPanelOpen, setIsNotificationPanelOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  // --- LOGICA CHAT TOGGLE ---
  const [isChatOpen, setIsChatOpen] = useState(true); // Default e deschis
  const toggleChat = () => setIsChatOpen(prev => !prev);

  // 1. Initializam notificările cu cele din mock data
  useEffect(() => {
    if (businessData) {
      setNotifications(MOCK_RESTAURANT_DATA.urgent_actions.map(n => ({...n, read: false, time: 'Acum'})));
    }
  }, [businessData]);

  // 2. Calculam cate sunt necitite
  useEffect(() => {
    setUnreadCount(notifications.filter(n => !n.read).length);
  }, [notifications]);

  // 3. POLLING SYSTEM (Simulare: Primim o notificare nouă la fiecare 15 secunde)
  useEffect(() => {
    if (!businessData) return;

    const interval = setInterval(() => {
      const newNotification = {
        id: Date.now(),
        title: "Alertă Nouă Agent",
        desc: "Monitoring Agent a detectat o anomalie în consumul de energie.",
        type: Math.random() > 0.5 ? 'warning' : 'info',
        read: false,
        time: 'Chiar acum'
      };
      
      // Adaugam notificarea noua la inceputul listei
      setNotifications(prev => [newNotification, ...prev]);
    }, 15000); // 15 secunde

    return () => clearInterval(interval);
  }, [businessData]);

  // Actiuni
  const toggleNotifications = () => setIsNotificationPanelOpen(prev => !prev);
  
  const markAsRead = (id) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  // --- LOGICA VECHE DE ONBOARDING ---
  const startNewBusiness = async (description) => {
    setIsLoading(true);
    setTimeout(() => {
      setBusinessData({
        name: "Business Nou",
        type: "restaurant",
        stage: "startup",
        details: description
      });
      setIsLoading(false);
    }, 1500);
  };

  const connectExistingBusiness = async (formData) => {
    setIsLoading(true);
    setTimeout(() => {
      setBusinessData({
        name: formData.name,
        type: "restaurant",
        cui: formData.cui,
        stage: "active"
      });
      setIsLoading(false);
    }, 1000);
  };

  return (
    <BusinessContext.Provider value={{ 
      // ... celelalte valori
      businessData,
      isLoading,
      notifications,
      
      // EXPORTAM NOILE VALORI:
      isChatOpen,
      toggleChat,
      
      // ... restul
      startNewBusiness, connectExistingBusiness, toggleNotifications, markAsRead, markAllAsRead
    }}>
      {children}
    </BusinessContext.Provider>
  );
};

export const useBusiness = () => useContext(BusinessContext);