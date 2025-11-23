import React from 'react';
import { LayoutDashboard, Package, Scale, Wallet, Bell, FileText } from 'lucide-react'; // Am adaugat FileText
import { NavLink } from 'react-router-dom';
import { useBusiness } from '../context/BusinessContext';

export default function Sidebar() {
  const { unreadCount, toggleNotifications } = useBusiness();

  const menuItems = [
    { icon: LayoutDashboard, label: 'General', path: '/' },
    { icon: Package, label: 'Inventar', path: '/inventory' },
    { icon: Wallet, label: 'Finanțe', path: '/finance' },
    { icon: Scale, label: 'Legal', path: '/legal' },
    { icon: FileText, label: 'Documente', path: '/documents' }, // <--- PAGINA NOUA
  ];

  return (
    <div className="w-20 md:w-64 bg-slate-900 text-white flex flex-col h-screen sticky top-0 shrink-0 transition-all duration-300">
      <div className="p-6 flex items-center gap-3">
        <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center font-bold text-lg shrink-0">B</div>
        <span className="font-bold text-xl hidden md:block whitespace-nowrap">BizGenie</span>
      </div>

      <nav className="flex-1 px-4 space-y-2 mt-4 overflow-y-auto">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `
              flex items-center gap-3 px-4 py-3 rounded-xl transition-all whitespace-nowrap
              ${isActive ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}
            `}
          >
            <item.icon className="w-5 h-5 shrink-0" />
            <span className="hidden md:block font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Notification Area */}
      <div className="p-4 mt-auto">
        <button 
          onClick={toggleNotifications}
          className="w-full bg-slate-800 rounded-xl p-4 flex items-center gap-3 cursor-pointer hover:bg-slate-700 transition group relative"
        >
          <div className="relative shrink-0">
            <Bell className="w-5 h-5 text-slate-400 group-hover:text-yellow-400 transition-colors" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 border-2 border-slate-800 rounded-full"></span>
            )}
          </div>
          <div className="hidden md:block text-left overflow-hidden">
            <p className="text-xs text-slate-400 truncate">Centru Alerte</p>
            <p className="text-sm font-bold text-white truncate">
              {unreadCount > 0 ? `${unreadCount} Noi` : 'Nicio alertă'}
            </p>
          </div>
        </button>
      </div>
    </div>
  );
}