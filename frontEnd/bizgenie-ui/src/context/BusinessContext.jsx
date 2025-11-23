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

	// Chat UI (Starea vizuala: deschis/inchis)
	const [isChatOpen, setIsChatOpen] = useState(true);

	// Inventar
	const [inventoryItems, setInventoryItems] = useState(MOCK_RESTAURANT_DATA.inventory);

	// MESAJE CHAT (ACUM SUNT GLOBALE)
	const [chatMessages, setChatMessages] = useState([
		{ id: 1, text: "Salut! Sunt BizGenie. Monitorizez activitatea.", sender: 'ai' }
	]);

	// Helper pentru a adăuga un mesaj în lista globală
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

	// Initializare notificari
	useEffect(() => {
		if (businessData) {
			setNotifications(MOCK_RESTAURANT_DATA.urgent_actions.map(n => ({ ...n, read: false, time: 'Acum' })));
		}
	}, [businessData]);

	useEffect(() => {
		setUnreadCount(notifications.filter(n => !n.read).length);
	}, [notifications]);


	// --- POLLING SYSTEM (PRIMIRE DATE AUTOMATE) ---
	useEffect(() => {
		const interval = setInterval(async () => {
			try {
				// 1. Cerem update-uri de la Proxy
				const updates = await BusinessService.checkUpdates();

				if (updates && updates.length > 0) {
					console.log("🔥 [UI] Update primit:", updates.length);

					updates.forEach(packet => {

						// CAZUL 1: Actualizare Inventar
						if (packet.type === 'data_update' && packet.payload.category === 'inventory') {
							console.log("📦 [UI] Update Inventar:", packet.payload.items);
							setInventoryItems(packet.payload.items);
						}

						// CAZUL 2: Mesaj Chat
						if (packet.type === 'chat_message') {
							console.log("💬 [UI] Mesaj Chat:", packet.payload.text);
							addChatMessage(packet.payload.text, 'ai');
						}

						// CAZUL 3: NOTIFICARE (AICI E MODIFICAREA!)
						if (packet.type === 'notification') {
							console.log("🔔 [UI] Adaug notificare în listă:", packet.payload.title);

							// Construim obiectul notificării
							const newNotification = {
								id: Date.now() + Math.random(), // ID unic
								title: packet.payload.title,
								desc: packet.payload.desc,
								type: packet.payload.type || 'info', // critical, warning, info
								time: 'Chiar acum',
								read: false,
								agent: 'System'
							};

							// O adăugăm la începutul listei existente (prev)
							setNotifications(prev => [newNotification, ...prev]);

							// (Opțional) Putem reda un sunet scurt aici dacă vrei pe viitor
						}

					});
				}
			} catch (e) {
				console.error("Polling error", e);
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
	const deleteNotification = (id) => { setNotifications(prev => prev.filter(n => n.id !== id)); };

	// Chat & Mesaje
	const toggleChat = () => setIsChatOpen(prev => !prev);

	const sendMessage = async (msg) => {
		return await BusinessService.sendMessage(msg, {});
	};


	// ==========================================
	// 4. PROVIDER
	// ==========================================
	return (
		<BusinessContext.Provider value={{
			businessData, isLoading, startNewBusiness, connectExistingBusiness,
			notifications, unreadCount, isNotificationPanelOpen, toggleNotifications, markAsRead, markAllAsRead, deleteNotification,

			// Exportam tot ce tine de chat
			isChatOpen, toggleChat,
			chatMessages, addChatMessage, sendMessage, // <--- IMPORTANTE

			inventoryItems, setInventoryItems
		}}>
			{children}
		</BusinessContext.Provider>
	);
};

export const useBusiness = () => useContext(BusinessContext);