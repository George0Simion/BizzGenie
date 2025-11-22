import React, { useState, useRef, useEffect } from 'react';
import { BusinessService } from '../services/api';
import { useBusiness } from '../context/BusinessContext';
import { Send, Bot, Loader2, Sparkles, X } from 'lucide-react';

export default function ChatWidget() {
	const { businessData, toggleChat } = useBusiness();
	const [messages, setMessages] = useState([
		{ id: 1, text: "Salut! Sunt BizGenie. Monitorizez activitatea restaurantului. Cu ce începem?", sender: 'ai' }
	]);
	const [input, setInput] = useState('');
	const [isTyping, setIsTyping] = useState(false);

	// Referinta pentru a face scroll automat jos
	const messagesEndRef = useRef(null);

	// Functia de scroll
	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	};

	useEffect(() => {
		scrollToBottom();
	}, [messages, isTyping]); // Se activeaza cand apar mesaje noi sau scrie AI-ul

	const handleSend = async (e) => {
		e.preventDefault();
		if (!input.trim()) return;

		const userText = input;
		setInput(''); // Golim inputul imediat

		// 1. Adaugam mesajul userului in UI
		const userMsg = { id: Date.now(), text: userText, sender: 'user' };
		setMessages(prev => [...prev, userMsg]);
		setIsTyping(true); // Apare animatia de incarcare

		try {
			// 2. Trimitem la Backend (impreuna cu datele business-ului)
			const response = await BusinessService.sendMessage(userText, businessData);

			// 3. Adaugam raspunsul AI in UI
			setMessages(prev => [...prev, {
				id: Date.now() + 1,
				text: response.text,
				sender: 'ai'
			}]);
		} catch (error) {
			// Eroare vizuala
			setMessages(prev => [...prev, {
				id: Date.now() + 1,
				text: "Nu pot comunica cu serverul momentan. Încearcă mai târziu.",
				sender: 'ai',
				isError: true
			}]);
		} finally {
			setIsTyping(false); // Oprim animatia
		}
	};

	return (
		<div className="flex flex-col h-full bg-white border-l border-slate-200 w-80 md:w-96 shadow-xl z-20">
			{/* Header */}
			<div className="p-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center h-16">

				{/* GRUPUL DIN STANGA: Iconita + Text */}
				<div className="flex items-center gap-3">
					<div className="p-2 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg shadow-blue-200 shadow-sm">
						<Sparkles className="w-4 h-4 text-white" />
					</div>
					<div className="flex flex-col justify-center">
						<h3 className="font-bold text-slate-800 text-sm leading-tight">AI Co-Pilot</h3>
						<div className="flex items-center gap-1.5 mt-0.5">
							<span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
							<span className="text-[10px] font-medium text-slate-500">Online</span>
						</div>
					</div>
				</div>

				{/* GRUPUL DIN DREAPTA: Butonul X */}
				<button
					onClick={toggleChat}
					className="p-2 text-slate-400 hover:text-red-600 hover:bg-white hover:shadow-sm rounded-lg transition-all"
					title="Închide"
				>
					<X className="w-5 h-5" />
				</button>

			</div>

			{/* Lista de Mesaje */}
			<div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/30 scroll-smooth">
				{messages.map((msg) => (
					<div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
						{msg.sender === 'ai' && (
							<div className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center mr-2 mt-1 shrink-0">
								<Bot className="w-4 h-4 text-indigo-600" />
							</div>
						)}

						<div className={`max-w-[85%] p-3 rounded-2xl text-sm leading-relaxed shadow-sm ${msg.sender === 'user'
							? 'bg-blue-600 text-white rounded-tr-none'
							: msg.isError
								? 'bg-red-50 text-red-600 border border-red-100'
								: 'bg-white border border-slate-200 text-slate-700 rounded-tl-none'
							}`}>
							{msg.text}
						</div>
					</div>
				))}

				{/* Typing Indicator */}
				{isTyping && (
					<div className="flex justify-start items-center gap-2">
						<div className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center mr-2">
							<Loader2 className="w-3 h-3 text-indigo-600 animate-spin" />
						</div>
						<div className="bg-slate-100 rounded-full px-4 py-2 flex gap-1">
							<span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
							<span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
							<span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
						</div>
					</div>
				)}

				{/* Ancora invizibila pentru scroll */}
				<div ref={messagesEndRef} />
			</div>

			{/* Input Area */}
			<div className="p-4 bg-white border-t border-slate-100">
				<form onSubmit={handleSend} className="relative">
					<input
						type="text"
						value={input}
						onChange={(e) => setInput(e.target.value)}
						disabled={isTyping}
						placeholder="Întreabă despre vânzări, stocuri..."
						className="w-full pl-4 pr-12 py-3 bg-slate-100 border-transparent focus:bg-white border focus:border-blue-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all text-sm disabled:opacity-50"
					/>
					<button
						type="submit"
						disabled={!input.trim() || isTyping}
						className="absolute right-2 top-2 p-1.5 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white rounded-lg transition-colors"
					>
						<Send className="w-4 h-4" />
					</button>
				</form>
			</div>
		</div>
	);
}