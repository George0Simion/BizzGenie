import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { BusinessProvider, useBusiness } from './context/BusinessContext';
import Sidebar from './components/Sidebar';
import ChatWidget from './components/ChatWidget';
import Dashboard from './pages/Dashboard';
import Onboarding from './pages/Onboarding';
import Inventory from './pages/Inventory';
import NotificationDrawer from './components/NotificationDrawer';
import Finance from './pages/Finance';
import Legal from './pages/Legal';
import { MessageCircle, Menu, X } from 'lucide-react';

// 1. Componenta de protecție (Dacă nu ai business, mergi la Onboarding)
const ProtectedRoute = ({ children }) => {
	const { businessData } = useBusiness();
	if (!businessData) {
		return <Navigate to="/onboarding" replace />;
	}
	return children;
};

// 2. Layout-ul Principal (AICI ERA PROBLEMA)
// Trebuie să fie un container Flex care ocupă tot ecranul (h-screen)
const MainLayout = ({ children }) => {
  // Aducem starea din context
  const { isChatOpen, toggleChat } = useBusiness();
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);

  const toggleMobileNav = () => setIsMobileNavOpen((prev) => !prev);
  const closeMobileNav = () => setIsMobileNavOpen(false);

  return (
    <div className="relative flex min-h-screen w-full flex-col bg-slate-50 overflow-x-hidden lg:flex-row">
      {/* Mobile top bar */}
      <div className="lg:hidden sticky top-0 z-30 flex items-center justify-between bg-white px-4 py-3 border-b border-slate-200 shadow-sm">
        <div className="flex items-center gap-3">
          <button
            onClick={toggleMobileNav}
            className="p-2 rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition"
            aria-label={isMobileNavOpen ? 'Închide meniul' : 'Deschide meniul'}
          >
            {isMobileNavOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-lg text-white">B</div>
            <div>
              <p className="text-sm text-slate-500 leading-tight">BizGenie</p>
              <p className="text-xs text-slate-400 leading-tight">Dashboard</p>
            </div>
          </div>
        </div>

        <button
          onClick={toggleChat}
          className="inline-flex items-center gap-2 rounded-xl px-3 py-2 bg-blue-600 text-white text-sm font-semibold shadow hover:bg-blue-700 transition active:scale-95"
        >
          <MessageCircle className="w-5 h-5" />
          <span className="hidden sm:inline">Chat</span>
        </button>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {/* Mobile sidebar drawer */}
      {isMobileNavOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={closeMobileNav}></div>
          <div className="relative h-full w-72 max-w-[80%] shadow-2xl">
            <Sidebar mode="mobile" onNavigate={closeMobileNav} />
          </div>
        </div>
      )}

      <main className="flex-1 w-full relative z-0 overflow-x-hidden pb-20 lg:overflow-y-auto">
        {children}
        
        {/* BUTON PLUTITOR (Apare doar cand chat-ul e INCHIS) */}
        {!isChatOpen && (
          <button 
            onClick={toggleChat}
            className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-xl hover:shadow-2xl transition-all transform hover:scale-110 z-50 flex items-center gap-2"
          >
            <MessageCircle className="w-6 h-6" />
            <span className="font-bold pr-1">Chat AI</span>
          </button>
        )}
      </main>

      <NotificationDrawer />

      {/* Chat overlay for small screens */}
      {isChatOpen && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-30 lg:hidden"
          onClick={toggleChat}
        ></div>
      )}
      {/* CHAT WIDGET (Apare doar cand isChatOpen e TRUE) */}
      {isChatOpen && <ChatWidget />}
      
    </div>
  );
};

// Placeholder pentru pagini în lucru
const WorkInProgress = ({ title }) => (
	<div className="p-10 text-center">
		<h2 className="text-2xl font-bold text-slate-300">{title}</h2>
		<p className="text-slate-400">Modul în dezvoltare...</p>
	</div>
);

// Rutele aplicației
const AppRoutes = () => {
	const { businessData } = useBusiness();

	return (
		<Routes>
			<Route path="/onboarding" element={
				businessData ? <Navigate to="/" replace /> : <Onboarding />
			} />

			<Route path="/" element={
				<ProtectedRoute>
					<MainLayout>
						<Dashboard />
					</MainLayout>
				</ProtectedRoute>
			} />

			<Route path="/inventory" element={
				<ProtectedRoute>
					<MainLayout>
						<Inventory />
					</MainLayout>
				</ProtectedRoute>
			} />

			<Route path="/finance" element={
				<ProtectedRoute>
					<MainLayout>
						<Finance />
					</MainLayout>
				</ProtectedRoute>
			} />

			<Route path="/legal" element={
				<ProtectedRoute>
					<MainLayout>
						<Legal />
					</MainLayout>
				</ProtectedRoute>
			} />
		</Routes>
	);
};

function App() {
  return (
    <BrowserRouter>
      <BusinessProvider>
        <AppRoutes />
      </BusinessProvider>
    </BrowserRouter>
  );
}

export default App;
