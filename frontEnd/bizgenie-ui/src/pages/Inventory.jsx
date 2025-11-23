import React from 'react';
import { useBusiness } from '../context/BusinessContext';
import { Package, Wifi } from 'lucide-react';

export default function Inventory() {
  // Luam datele din context. Contextul se actualizeaza singur la fiecare 2 secunde.
  const { inventoryItems } = useBusiness();

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2 text-slate-800">
            <Package className="text-blue-600" /> 
            Monitorizare Inventar
          </h1>
          <p className="text-slate-500 text-sm">Datele sunt sincronizate automat cu serverul.</p>
        </div>
        
        {/* Indicator vizual ca sistemul e LIVE */}
        <div className="flex items-center gap-2 px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold animate-pulse">
          <Wifi className="w-3 h-3" />
          LIVE UPDATE
        </div>
      </div>

      {/* Tabel simplu */}
      <div className="bg-white rounded-xl shadow border border-slate-200 overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-50 border-b">
            <tr>
              <th className="p-4 text-slate-500 font-semibold text-sm">ID</th>
              <th className="p-4 text-slate-500 font-semibold text-sm">Produs</th>
              <th className="p-4 text-slate-500 font-semibold text-sm">Stoc</th>
              <th className="p-4 text-slate-500 font-semibold text-sm">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {inventoryItems.map((item, idx) => (
              <tr key={idx} className="hover:bg-slate-50 transition-colors animate-in slide-in-from-bottom-2 duration-300">
                <td className="p-4 text-slate-400 text-sm">#{item.id || idx + 1}</td>
                <td className="p-4 font-bold text-slate-700">{item.name}</td>
                <td className="p-4 font-medium">{item.stock} {item.unit}</td>
                <td className="p-4">
                    <span className="bg-blue-50 text-blue-600 px-2 py-1 rounded text-xs font-bold">
                        Actualizat
                    </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {inventoryItems.length === 0 && (
            <div className="p-8 text-center text-slate-400">
                Se așteaptă date de la agenți...
            </div>
        )}
      </div>
    </div>
  );
}