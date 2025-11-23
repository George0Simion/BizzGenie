import React from 'react';
import { useBusiness } from '../context/BusinessContext';
import { Package, Wifi, AlertTriangle, CheckCircle, RefreshCw, ShoppingCart, Loader2, Server } from 'lucide-react';

export default function Inventory() {
  const { inventoryItems } = useBusiness();

  // --- LOADING STATE ---
  if (inventoryItems === null) {
      return (
        <div className="flex flex-col items-center justify-center h-[80vh] text-center p-6">
            <div className="relative mb-6">
                <Server className="w-16 h-16 text-slate-200" />
                <div className="absolute -bottom-2 -right-2 bg-white rounded-full p-1">
                    <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                </div>
            </div>
            <h2 className="text-2xl font-bold text-slate-800 mb-2">Se conectează la depozit...</h2>
            <p className="text-slate-500 max-w-md">
                Așteptăm datele în timp real de la Inventory Agent. 
                <br/>Verifică dacă simulatorul este pornit.
            </p>
        </div>
      );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2 text-slate-800">
            <Package className="text-blue-600" /> 
            Monitorizare Inventar
          </h1>
          <p className="text-slate-500 text-sm">Sincronizat cu baza de date ERP.</p>
        </div>
        
        <div className="flex items-center gap-2 px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold animate-pulse">
          <Wifi className="w-3 h-3" />
          LIVE DATA
        </div>
      </div>

      <div className="bg-white rounded-xl shadow border border-slate-200 overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-50 border-b">
            <tr>
              <th className="p-4 text-slate-500 font-semibold text-xs uppercase">ID</th>
              <th className="p-4 text-slate-500 font-semibold text-xs uppercase">Produs / Categorie</th>
              <th className="p-4 text-slate-500 font-semibold text-xs uppercase">Stoc</th>
              <th className="p-4 text-slate-500 font-semibold text-xs uppercase">Expirare</th>
              <th className="p-4 text-slate-500 font-semibold text-xs uppercase">Status</th>
              <th className="p-4 text-slate-500 font-semibold text-xs uppercase">Auto-Buy</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {inventoryItems.map((item, idx) => {
              const isLowStock = item.quantity < item.min_threshold;

              return (
                <tr key={idx} className="hover:bg-slate-50 transition-colors">
                  <td className="p-4 text-slate-400 text-xs font-mono">#{item.id}</td>
                  
                  <td className="p-4">
                    <div className="font-bold text-slate-800 capitalize">{item.product_name}</div>
                    <div className="text-xs text-slate-500 bg-slate-100 inline-block px-1.5 py-0.5 rounded capitalize mt-1">
                      {item.category}
                    </div>
                  </td>
                  
                  <td className="p-4">
                    <div className={`font-mono font-bold ${isLowStock ? 'text-red-600' : 'text-slate-700'}`}>
                        {item.quantity} {item.unit}
                    </div>
                    <div className="text-[10px] text-slate-400">
                        Min: {item.min_threshold} {item.unit}
                    </div>
                  </td>

                  <td className="p-4 text-sm text-slate-600">
                    {item.expiration_date}
                  </td>

                  <td className="p-4">
                    {isLowStock ? (
                       <span className="flex items-center gap-1 text-xs font-bold text-red-600 bg-red-50 px-2 py-1 rounded-full w-fit">
                         <AlertTriangle className="w-3 h-3" /> CRITIC
                       </span>
                    ) : (
                       <span className="flex items-center gap-1 text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full w-fit">
                         <CheckCircle className="w-3 h-3" /> OK
                       </span>
                    )}
                  </td>

                  <td className="p-4">
                    {item.auto_buy === 1 ? (
                        <div className="text-blue-600" title="Auto-buy activ">
                            <RefreshCw className="w-4 h-4" />
                        </div>
                    ) : (
                        <div className="text-slate-300" title="Manual">
                            <ShoppingCart className="w-4 h-4" />
                        </div>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        
        {inventoryItems.length === 0 && (
            <div className="p-12 text-center text-slate-400 flex flex-col items-center">
                <Package className="w-12 h-12 text-slate-200 mb-2" />
                <p>Inventarul este gol momentan.</p>
            </div>
        )}
      </div>
    </div>
  );
}