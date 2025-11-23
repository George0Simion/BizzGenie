import React from 'react';
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
import { MessageCircle } from 'lucide-react';

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

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden w-full relative">
      
      <Sidebar />
      
      <main className="flex-1 overflow-y-auto h-full relative z-0">
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