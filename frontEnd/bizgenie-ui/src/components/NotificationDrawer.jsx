import React from 'react';
import { X, Bell, AlertTriangle, Info, AlertOctagon, Trash2 } from 'lucide-react';
import { useBusiness } from '../context/BusinessContext';

export default function NotificationDrawer() {
  const { 
    isNotificationPanelOpen, 
    toggleNotifications, 
    notifications, 
    markAsRead,
    markAllAsRead,
    deleteNotification
  } = useBusiness();

  if (!isNotificationPanelOpen) return null;

  return (
    <div className="absolute inset-0 z-50 flex justify-end">
      {/* Overlay */}
      <div 
        className="absolute inset-0 bg-black/20 backdrop-blur-sm transition-opacity"
        onClick={toggleNotifications}
      ></div>

      {/* Panel */}
      <div className="relative w-full max-w-md bg-white h-full shadow-2xl animate-in slide-in-from-right duration-300 flex flex-col">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50">
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-slate-700" />
            <h2 className="font-bold text-slate-800 text-lg">Notificări</h2>
            <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full font-bold">
              {notifications.length}
            </span>
          </div>
          <div className="flex gap-2">
            <button 
              onClick={markAllAsRead}
              className="text-xs text-blue-600 font-medium hover:underline px-2 py-1"
            >
              Citește tot
            </button>
            <button 
              onClick={toggleNotifications}
              className="p-1 hover:bg-slate-200 rounded-full transition-colors"
            >
              <X className="w-5 h-5 text-slate-500" />
            </button>
          </div>
        </div>

        {/* Lista Notificari */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/50">
          {notifications.length === 0 ? (
            <div className="text-center text-slate-400 py-10 flex flex-col items-center">
              <Bell className="w-12 h-12 text-slate-200 mb-2" />
              <p>Nicio notificare activă.</p>
            </div>
          ) : (
            notifications.map((notif) => (
              <div 
                key={notif.id} 
                onClick={() => markAsRead(notif.id)}
                className={`p-4 rounded-xl border transition-all cursor-pointer relative group ${
                  notif.read 
                    ? 'bg-white border-slate-100 opacity-60 hover:opacity-100' 
                    : 'bg-white border-blue-100 shadow-sm border-l-4 border-l-blue-500'
                }`}
              >
                <div className="flex gap-3 items-start pr-6">
                  
                  {/* Iconita */}
                  <div className={`mt-1 p-1.5 rounded-full shrink-0 ${
                    notif.type === 'critical' ? 'bg-red-100 text-red-600' :
                    notif.type === 'warning' ? 'bg-amber-100 text-amber-600' :
                    'bg-blue-100 text-blue-600'
                  }`}>
                    {notif.type === 'critical' ? <AlertOctagon className="w-4 h-4" /> :
                     notif.type === 'warning' ? <AlertTriangle className="w-4 h-4" /> :
                     <Info className="w-4 h-4" />}
                  </div>
                  
                  {/* Text */}
                  <div>
                    <h4 className={`text-sm font-bold ${notif.read ? 'text-slate-600' : 'text-slate-900'}`}>
                      {notif.title}
                    </h4>
                    <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                      {notif.desc}
                    </p>
                    <p className="text-[10px] text-slate-400 mt-2 font-medium uppercase tracking-wide flex justify-between w-full">
                      <span>{notif.time}</span>
                      <span>• Agent: {notif.agent}</span>
                    </p>
                  </div>
                </div>

                {/* Butonul de STERGERE (Acum e singur in colt) */}
                <button 
                    onClick={(e) => {
                        e.stopPropagation();
                        deleteNotification(notif.id);
                    }}
                    className="absolute top-2 right-2 p-1.5 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                    title="Șterge"
                >
                    <Trash2 className="w-4 h-4" />
                </button>

                {/* AM ELIMINAT BULINA ALBASTRĂ DE AICI */}
              </div>
            ))
          )}
        </div>

      </div>
    </div>
  );
}