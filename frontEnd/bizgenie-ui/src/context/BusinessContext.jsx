import React, { createContext, useState, useContext, useEffect } from 'react';
import { BusinessService } from '../services/api';
import { MOCK_RESTAURANT_DATA } from '../data/mockData';

const BusinessContext = createContext();

export const BusinessProvider = ({ children }) => {
  // STATE
  const [businessData, setBusinessData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [isNotificationPanelOpen, setIsNotificationPanelOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isChatOpen, setIsChatOpen] = useState(true);
  const [chatMessages, setChatMessages] = useState([{ id: 1, text: "Salut! Sunt BizGenie. Aștept conexiunea cu serverele...", sender: 'ai' }]);
  
  const [inventoryItems, setInventoryItems] = useState(null);
  const [legalTasks, setLegalTasks] = useState(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const addChatMessage = (text, sender = 'ai') => {
    setChatMessages(prev => [...prev, { id: Date.now() + Math.random(), text, sender }]);
  };

  // INITIALIZARE
  useEffect(() => {
    if (businessData) {
      setNotifications(MOCK_RESTAURANT_DATA.urgent_actions.map(n => ({...n, read: false, time: 'Acum'})));
    }
  }, [businessData]);

  useEffect(() => {
    setUnreadCount(notifications.filter(n => !n.read).length);
  }, [notifications]);

  // POLLING SYSTEM
  useEffect(() => {
    const checkForUpdates = async () => {
      try {
        const updates = await BusinessService.checkUpdates();
        if (updates && updates.length > 0) {
          updates.forEach(packet => {
            
            if (packet.type === 'data_update' && packet.payload.category === 'inventory') {
              setInventoryItems(packet.payload.items);
            }
            
            if (packet.type === 'data_update' && packet.payload.category === 'legal') {
                setLegalTasks(packet.payload.tasks);
            }

            if (packet.type === 'data_update' && packet.payload.category === 'legal_research') {
                const raw = packet.payload.data || packet.payload;
                const dataObj = raw || payload; 

                const subject = dataObj.subject || "Research";
                const summary = dataObj.summary || (dataObj.research && dataObj.research.summary) || "";
                const checklist = dataObj.checklist || (dataObj.research && dataObj.research.checklist) || [];
                const risks = dataObj.risks || (dataObj.research && dataObj.research.risks) || [];

                const newTask = {
                    id: Date.now(),
                    title: subject,
                    status: 'pending',
                    description: summary,
                    steps: checklist.map(item => ({
                        step: item.step,
                        action: item.action,
                        citation: item.citation,
                        source: item.source,
                        done: item.done || false
                    })),
                    risks: risks
                };
                
                setLegalTasks(prev => [newTask, ...(prev || [])]);
            }

            if (packet.type === 'chat_message') addChatMessage(packet.payload.text, 'ai');
            
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
      } catch (e) {}
    };

    checkForUpdates();
    const interval = setInterval(checkForUpdates, 2000);
    return () => clearInterval(interval);
  }, []);

  // EXPORTS & ACTIUNI

  // --- 1. START NEW BUSINESS (CURĂȚAT & SIMPLU) ---
  const startNewBusiness = async (description) => {
    setIsLoading(true);
    
    const newBiz = { 
        name: "Afacerea Mea (Startup)", 
        type: "startup", 
        stage: "ideation", 
        details: description 
    };

    // 1. Adăugăm mesajul userului în chat exact așa cum l-a scris
    addChatMessage(description, 'user');

    // 2. Trimitem mesajul la server pentru procesare
    try {
        // Nu mai adăugăm niciun text automat gen "Fa un plan..."
        await BusinessService.sendMessage(description, newBiz);
    } catch (e) {
        console.error("Eroare trimitere mesaj start:", e);
    }

    // 3. Intram în dashboard
    setTimeout(() => {
      setBusinessData(newBiz);
      setIsLoading(false);
    }, 1000);
  };

  const connectExistingBusiness = async (f) => { setIsLoading(true); setTimeout(() => { setBusinessData({name: f.name, type: "restaurant", cui: f.cui, stage: "active"}); setIsLoading(false); }, 1000); };
  
  const toggleNotifications = () => setIsNotificationPanelOpen(prev => !prev);
  const markAsRead = (id) => setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  const markAllAsRead = () => setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  const deleteNotification = (id) => setNotifications(prev => prev.filter(n => n.id !== id));
  
  const toggleChat = () => setIsChatOpen(prev => !prev);
  const sendMessage = async (msg) => await BusinessService.sendMessage(msg, {});
  const toggleMobileMenu = () => setIsMobileMenuOpen(prev => !prev);
  const closeMobileMenu = () => setIsMobileMenuOpen(false);

  const toggleLegalStep = (taskId, stepName) => {
    if (!legalTasks) return;
    setLegalTasks(prevTasks => prevTasks.map(task => {
      if (task.id !== taskId) return task;
      const updatedSteps = task.steps.map(s => s.step === stepName ? { ...s, done: !s.done } : s);
      const allDone = updatedSteps.every(s => s.done);
      const anyDone = updatedSteps.some(s => s.done);
      let newStatus = allDone ? 'completed' : (anyDone ? 'in_progress' : 'pending');
      return { ...task, steps: updatedSteps, status: newStatus };
    }));
  };
  
  const deleteLegalTask = (taskId) => {
      if (!legalTasks) return;
      setLegalTasks(prev => prev.filter(t => t.id !== taskId));
  };
  
  const saveLegalChanges = async () => { 
      try { 
          await BusinessService.saveLegalTasks(legalTasks || []); 
          addChatMessage("Modificări legale salvate.", "system"); 
      } catch(e) { throw e; } 
  };

  return (
    <BusinessContext.Provider value={{ 
      businessData, isLoading, startNewBusiness, connectExistingBusiness,
      notifications, unreadCount, isNotificationPanelOpen, toggleNotifications, markAsRead, markAllAsRead, deleteNotification,
      isChatOpen, toggleChat, chatMessages, addChatMessage, sendMessage,
      inventoryItems, setInventoryItems,
      legalTasks, setLegalTasks, toggleLegalStep, deleteLegalTask, saveLegalChanges,
      isMobileMenuOpen, toggleMobileMenu, closeMobileMenu
    }}>
      {children}
    </BusinessContext.Provider>
  );
};

export const useBusiness = () => useContext(BusinessContext);