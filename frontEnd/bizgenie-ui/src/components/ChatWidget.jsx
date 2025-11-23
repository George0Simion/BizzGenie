import React, { useState, useRef, useEffect } from 'react';
import { useBusiness } from '../context/BusinessContext';
import { Send, Bot, Loader2, Sparkles, X } from 'lucide-react';

export default function ChatWidget() {
    const { chatMessages, addChatMessage, sendMessage, toggleChat } = useBusiness();
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [chatMessages, isTyping]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;
        const userText = input;
        setInput('');
        addChatMessage(userText, 'user');
        setIsTyping(true);
        try {
            const response = await sendMessage(userText);
            if (response && response.text) addChatMessage(response.text, 'ai');
        } catch (error) {
            addChatMessage("Eroare: Nu pot contacta serverul.", 'ai');
        } finally { setIsTyping(false); }
    };

    return (
        // --- RESPONSIVE CLASSES: fixed pe mobile, static pe desktop ---
        <div className="fixed inset-0 z-[60] md:static md:z-auto flex flex-col h-full bg-white md:border-l border-slate-200 w-full md:w-96 shadow-xl">
            
            {/* Header */}
            <div className="p-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center h-16 shrink-0">
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
                <button onClick={toggleChat} className="p-2 text-slate-400 hover:text-red-600 hover:bg-white hover:shadow-sm rounded-lg transition-all">
                    <X className="w-6 h-6 md:w-5 md:h-5" />
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/30 scroll-smooth">
                {chatMessages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                        {msg.sender === 'ai' && (
                            <div className="w-8 h-8 md:w-6 md:h-6 bg-indigo-100 rounded-full flex items-center justify-center mr-2 mt-1 shrink-0">
                                <Bot className="w-5 h-5 md:w-4 md:h-4 text-indigo-600" />
                            </div>
                        )}
                        <div className={`max-w-[85%] p-3 rounded-2xl text-sm leading-relaxed shadow-sm ${msg.sender === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-white border border-slate-200 text-slate-700 rounded-tl-none'}`}>
                            {msg.text}
                        </div>
                    </div>
                ))}
                {isTyping && (
                    <div className="flex justify-start items-center gap-2">
                         <div className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center mr-2"><Loader2 className="w-3 h-3 text-indigo-600 animate-spin" /></div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 bg-white border-t border-slate-100 shrink-0">
                <form onSubmit={handleSend} className="relative flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={isTyping}
                        placeholder="Întreabă AI..."
                        className="flex-1 pl-4 pr-12 py-3 bg-slate-100 border-transparent focus:bg-white border focus:border-blue-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all text-sm"
                    />
                    <button type="submit" disabled={!input.trim() || isTyping} className="absolute right-2 top-2 p-1.5 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white rounded-lg transition-colors">
                        <Send className="w-4 h-4" />
                    </button>
                </form>
            </div>
        </div>
    );
}