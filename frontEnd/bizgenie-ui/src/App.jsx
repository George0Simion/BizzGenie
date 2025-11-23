import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { BusinessProvider, useBusiness } from './context/BusinessContext';
import { MessageCircle, Menu } from 'lucide-react';

import Sidebar from './components/Sidebar';
import ChatWidget from './components/ChatWidget';
import NotificationDrawer from './components/NotificationDrawer';

import Dashboard from './pages/Dashboard';
import Onboarding from './pages/Onboarding';
import Inventory from './pages/Inventory';
import Legal from './pages/Legal';
import Finance from './pages/Finance';
import Documents from './pages/Documents';

const ProtectedRoute = ({ children }) => {
  const { businessData } = useBusiness();
  if (!businessData) return <Navigate to="/onboarding" replace />;
  return children;
};

const MainLayout = ({ children }) => {
  const { isChatOpen, toggleChat, isMobileMenuOpen, toggleMobileMenu, closeMobileMenu } = useBusiness();

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden w-full relative">
      
      {/* 1. SIDEBAR DESKTOP (Ascuns pe mobil) */}
      <div className="hidden md:block h-full">
        <Sidebar />
      </div>

      {/* 2. SIDEBAR MOBILE (Cu Overlay) */}
      {isMobileMenuOpen && (
        <div 
            className="fixed inset-0 bg-black/50 z-40 md:hidden backdrop-blur-sm"
            onClick={closeMobileMenu}
        ></div>
      )}
      
      <div className={`fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-300 ease-in-out md:hidden ${
          isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <Sidebar />
      </div>


      {/* 3. ZONA CONTINUT */}
      <main className="flex-1 flex flex-col h-full overflow-hidden relative z-0">
        
        {/* HEADER MOBILE (Doar pe ecrane mici) */}
        <header className="md:hidden bg-white border-b border-slate-200 p-4 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-3">
                <button onClick={toggleMobileMenu} className="p-2 -ml-2 text-slate-600 hover:bg-slate-100 rounded-lg">
                    <Menu className="w-6 h-6" />
                </button>
                <span className="font-bold text-lg text-slate-800">BizGenie</span>
            </div>
        </header>

        {/* CONTENT SCROLLABIL */}
        <div className="flex-1 overflow-y-auto p-0">
            {children}
            <div className="h-20 md:h-0"></div> {/* Spacer pt mobil */}
        </div>

        {/* BUTON CHAT (Cand e inchis) */}
        {!isChatOpen && (
          <button 
            onClick={toggleChat}
            className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-xl hover:shadow-2xl transition-all transform hover:scale-110 z-40 flex items-center gap-2"
          >
            <MessageCircle className="w-6 h-6" />
            <span className="font-bold pr-1 hidden md:inline">Chat AI</span>
          </button>
        )}
      </main>

      <NotificationDrawer />
      {isChatOpen && <ChatWidget />}
    </div>
  );
};

const AppRoutes = () => {
  const { businessData } = useBusiness();
  return (
    <Routes>
      <Route path="/onboarding" element={businessData ? <Navigate to="/" replace /> : <Onboarding />} />
      <Route path="/" element={<ProtectedRoute><MainLayout><Dashboard /></MainLayout></ProtectedRoute>} />
      <Route path="/inventory" element={<ProtectedRoute><MainLayout><Inventory /></MainLayout></ProtectedRoute>} />
      <Route path="/finance" element={<ProtectedRoute><MainLayout><Finance /></MainLayout></ProtectedRoute>} />
      <Route path="/legal" element={<ProtectedRoute><MainLayout><Legal /></MainLayout></ProtectedRoute>} />
      <Route path="/documents" element={<ProtectedRoute><MainLayout><Documents /></MainLayout></ProtectedRoute>} />
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