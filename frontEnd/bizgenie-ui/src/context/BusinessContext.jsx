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
  const [chatMessages, setChatMessages] = useState([{ id: 1, text: "Salut! Sunt BizGenie.", sender: 'ai' }]);
  const [inventoryItems, setInventoryItems] = useState(MOCK_RESTAURANT_DATA.inventory);
  const [legalTasks, setLegalTasks] = useState([]);

  const addChatMessage = (text, sender = 'ai') => {
    setChatMessages(prev => [...prev, { id: Date.now() + Math.random(), text, sender }]);
  };

  // INIT
  useEffect(() => {
    if (businessData) {
      setNotifications(MOCK_RESTAURANT_DATA.urgent_actions.map(n => ({...n, read: false, time: 'Acum'})));
      if (MOCK_RESTAURANT_DATA.legal && MOCK_RESTAURANT_DATA.legal.checklist) {
          setLegalTasks(MOCK_RESTAURANT_DATA.legal.checklist);
      }
    }
  }, [businessData]);

  useEffect(() => {
    setUnreadCount(notifications.filter(n => !n.read).length);
  }, [notifications]);

  // POLLING
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const updates = await BusinessService.checkUpdates();
        if (updates && updates.length > 0) {
          updates.forEach(packet => {
            // 1. INVENTAR
            if (packet.type === 'data_update' && packet.payload.category === 'inventory') {
              setInventoryItems(packet.payload.items);
            }
            
            // 2. LEGAL STANDARD
            if (packet.type === 'data_update' && packet.payload.category === 'legal') {
                setLegalTasks(packet.payload.tasks);
            }

            // 3. LEGAL RESEARCH (NOU - FORMAT COMPLEX)
            if (packet.type === 'data_update' && packet.payload.category === 'legal_research') {
                const raw = packet.payload.data;
                console.log("⚖️ [UI] Research complex primit:", raw.subject);

                // Convertim structura complexa intr-un task compatibil cu UI-ul nostru
                const newTask = {
                    id: Date.now(),
                    title: raw.subject,
                    status: 'in_progress',
                    description: raw.research.summary,
                    // Mapam pasii pastrand metadatele (action, citation, source)
                    steps: raw.research.checklist.map(item => ({
                        step: item.step,
                        action: item.action,     // Extra info
                        citation: item.citation, // Extra info
                        source: item.source,     // Link
                        done: item.done || false
                    })),
                    // Stocam riscurile separat in obiectul task-ului
                    risks: raw.research.risks
                };
                setLegalTasks(prev => [newTask, ...prev]);
            }

            // 4. CHAT & NOTIFICARI
            if (packet.type === 'chat_message') addChatMessage(packet.payload.text, 'ai');
            if (packet.type === 'notification') {
               setNotifications(prev => [{
                  id: Date.now() + Math.random(), title: packet.payload.title, desc: packet.payload.desc,
                  type: packet.payload.type || 'info', time: 'Acum', read: false, agent: 'System'
               }, ...prev]);
            }
          });
        }
      } catch (e) {}
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // ACTIONS
  const startNewBusiness = async (d) => { setIsLoading(true); setTimeout(() => { setBusinessData({name: "New Biz", type: "restaurant"}); setIsLoading(false); }, 1000); };
  const connectExistingBusiness = async (f) => { setIsLoading(true); setTimeout(() => { setBusinessData({name: f.name, type: "restaurant"}); setIsLoading(false); }, 1000); };
  const toggleNotifications = () => setIsNotificationPanelOpen(prev => !prev);
  const markAsRead = (id) => setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  const markAllAsRead = () => setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  const deleteNotification = (id) => setNotifications(prev => prev.filter(n => n.id !== id));
  const toggleChat = () => setIsChatOpen(prev => !prev);
  const sendMessage = async (msg) => await BusinessService.sendMessage(msg, {});

  // LEGAL LOGIC
  const toggleLegalStep = (taskId, stepName) => {
    setLegalTasks(prevTasks => prevTasks.map(task => {
      if (task.id !== taskId) return task;
      const updatedSteps = task.steps.map(s => s.step === stepName ? { ...s, done: !s.done } : s);
      const allDone = updatedSteps.every(s => s.done);
      const anyDone = updatedSteps.some(s => s.done);
      let newStatus = allDone ? 'completed' : (anyDone ? 'in_progress' : 'pending');
      return { ...task, steps: updatedSteps, status: newStatus };
    }));
  };

  const deleteLegalTask = (taskId) => setLegalTasks(prev => prev.filter(t => t.id !== taskId));
  const saveLegalChanges = async () => { try { await BusinessService.saveLegalTasks(legalTasks); addChatMessage("Modificări legale salvate.", "system"); } catch(e) { throw e; } };

  return (
    <BusinessContext.Provider value={{ 
      businessData, isLoading, startNewBusiness, connectExistingBusiness,
      notifications, unreadCount, isNotificationPanelOpen, toggleNotifications, markAsRead, markAllAsRead, deleteNotification,
      isChatOpen, toggleChat, chatMessages, addChatMessage, sendMessage,
      inventoryItems, setInventoryItems,
      legalTasks, setLegalTasks, toggleLegalStep, deleteLegalTask, saveLegalChanges
    }}>
      {children}
    </BusinessContext.Provider>
  );
};

export const useBusiness = () => useContext(BusinessContext);