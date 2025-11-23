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

	// Legal tasks (list of tasks/steps/risks)
	const [legalTasks, setLegalTasks] = useState([]);

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

						// CAZUL 1b: Actualizare Legal (research) -> mapam in legalTasks
						if (packet.type === 'data_update' && packet.payload.category === 'legal') {
							setLegalTasks(packet.payload.tasks || []);
						}

						if (packet.type === 'data_update' && packet.payload.category === 'legal_research') {
							const rawPayload = packet.payload.data ? packet.payload.data : packet.payload;
							const entries = Array.isArray(rawPayload) ? rawPayload : [rawPayload];
							console.log("⚖️ [UI] Research complex primit:", entries.length);

							const mappedTasks = entries.map(raw => ({
								id: Date.now() + Math.random(),
								title: raw.subject || "Analiză legală",
								status: 'pending',
								description: raw.research?.summary || raw.summary || "",
								steps: (raw.research?.checklist || raw.checklist || []).map(item => ({
									step: item.step,
									action: item.action,
									citation: item.citation,
									source: item.source,
									done: item.done || false
								})),
								risks: raw.research?.risks || raw.risks || []
							}));

							// dacă payload-ul trimite un set explicit (liste), le înlocuim,
							// altfel le adăugăm la istoric (max 20)
							if (Array.isArray(rawPayload) && rawPayload.length > 1) {
								setLegalTasks(mappedTasks.slice(0, 20));
							} else {
								setLegalTasks(prev => [...mappedTasks, ...prev].slice(0, 20));
							}
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

	// Legal task helpers
	const toggleLegalStep = (taskId, stepName) => {
		setLegalTasks(prevTasks => prevTasks.map(task => {
			if (task.id !== taskId) return task;
			const updatedSteps = (task.steps || []).map(s => s.step === stepName ? { ...s, done: !s.done } : s);
			const allDone = updatedSteps.every(s => s.done);
			const anyDone = updatedSteps.some(s => s.done);
			const newStatus = allDone ? 'completed' : (anyDone ? 'in_progress' : 'pending');
			return { ...task, steps: updatedSteps, status: newStatus };
		}));
	};

	const deleteLegalTask = (taskId) => setLegalTasks(prev => prev.filter(t => t.id !== taskId));

	const saveLegalChanges = async () => {
		try {
			await BusinessService.saveLegalTasks(legalTasks);
			addChatMessage("Modificări legale salvate.", "system");
		} catch (e) {
			console.error("Eroare la salvarea task-urilor legale", e);
			throw e;
		}
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

			inventoryItems, setInventoryItems,
			legalTasks, setLegalTasks, toggleLegalStep, deleteLegalTask, saveLegalChanges
		}}>
			{children}
		</BusinessContext.Provider>
	);
};

export const useBusiness = () => useContext(BusinessContext);
