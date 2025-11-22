import React, { useState } from 'react';
import { MOCK_RESTAURANT_DATA } from '../data/mockData';
import { Search, Plus, Filter, AlertTriangle, CheckCircle, Package } from 'lucide-react';

export default function Inventory() {
  // Luam lista initiala din mock data
  const [items, setItems] = useState(MOCK_RESTAURANT_DATA.inventory);
  const [searchTerm, setSearchTerm] = useState('');

  // Filtrare simpla dupa nume
  const filteredItems = items.filter(item => 
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 max-w-6xl mx-auto h-full flex flex-col">
      
      {/* Header Pagina */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Package className="w-6 h-6 text-blue-600" />
            Gestiune Inventar
          </h1>
          <p className="text-slate-500">Monitorizează stocurile și datele de expirare.</p>
        </div>
        
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl font-medium flex items-center gap-2 transition-colors shadow-sm">
          <Plus className="w-4 h-4" />
          Adaugă Produs
        </button>
      </div>

      {/* Toolbar (Search & Filter) */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm mb-6 flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
          <input 
            type="text" 
            placeholder="Caută ingredient..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
        </div>
        <button className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 font-medium text-sm">
          <Filter className="w-4 h-4" />
          Filtrează
        </button>
      </div>

      {/* Tabelul de Produse */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex-1">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Produs</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Cantitate</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Expirare</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Acțiuni</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredItems.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="font-semibold text-slate-800">{item.name}</div>
                    <div className="text-xs text-slate-400">ID: #{item.id}</div>
                  </td>
                  <td className="px-6 py-4 font-medium text-slate-700">
                    {item.stock} <span className="text-slate-400 text-xs">{item.unit}</span>
                  </td>
                  <td className="px-6 py-4 text-slate-600 text-sm">
                    {item.expiry}
                  </td>
                  <td className="px-6 py-4">
                    {item.status === 'critical' ? (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-red-100 text-red-700 border border-red-200">
                        <AlertTriangle className="w-3 h-3" /> CRITIC
                      </span>
                    ) : item.status === 'warning' ? (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200">
                        <AlertTriangle className="w-3 h-3" /> SCĂZUT
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700 border border-emerald-200">
                        <CheckCircle className="w-3 h-3" /> OK
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <button className="text-blue-600 hover:text-blue-800 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                      Editează
                    </button>
                  </td>
                </tr>
              ))}
              
              {/* Mesaj daca nu gasim nimic */}
              {filteredItems.length === 0 && (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center text-slate-500">
                    Nu am găsit niciun produs conform căutării.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}