import React, { useState } from 'react';
import { MOCK_RESTAURANT_DATA } from '../data/mockData';
import { useBusiness } from '../context/BusinessContext'; // <--- IMPORTAM CONTEXTUL
import { TrendingUp, Users, AlertOctagon, Lightbulb, Building2 } from 'lucide-react';

export default function Dashboard() {
  // 1. Luăm datele reale introduse de tine (nume, CUI etc.)
  const { businessData } = useBusiness();
  
  // 2. Luăm datele simulate (statistici, grafice) - care vor veni din backend mai târziu
  const [data] = useState(MOCK_RESTAURANT_DATA);

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      
      {/* HEADER DINAMIC - Aici folosim numele tău */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between border-b border-slate-200 pb-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-2">
            {businessData?.name || "Afacerea Ta"} 
          </h1>
          <div className="flex flex-wrap gap-3 mt-2 text-slate-500 text-sm">
            <span className="flex items-center gap-1">
              <Building2 className="w-4 h-4" />
              {businessData?.type === 'restaurant' ? 'Restaurant & Horeca' : 'Business General'}
            </span>
            {businessData?.cui && <span>• CUI: {businessData.cui}</span>}
          </div>
        </div>
        <span className="bg-green-100 text-green-700 px-4 py-1.5 rounded-full text-sm font-bold shadow-sm">
          ● Open for Business
        </span>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-slate-500 text-sm font-medium uppercase tracking-wider">Vânzări Azi</p>
              <h3 className="text-3xl font-bold text-slate-800 mt-2">{data.stats.revenue}</h3>
            </div>
            <div className="p-3 bg-emerald-50 rounded-xl"><TrendingUp className="text-emerald-600" /></div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-slate-500 text-sm font-medium uppercase tracking-wider">Grad Ocupare</p>
              <h3 className="text-3xl font-bold text-slate-800 mt-2">{data.stats.occupancy}</h3>
            </div>
            <div className="p-3 bg-blue-50 rounded-xl"><Users className="text-blue-600" /></div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-slate-500 text-sm font-medium uppercase tracking-wider">Stoc Critic</p>
              <h3 className="text-3xl font-bold text-red-600 mt-2">{data.stats.lowStockItems} produse</h3>
            </div>
            <div className="p-3 bg-red-50 rounded-xl"><AlertOctagon className="text-red-600" /></div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Urgent Actions */}
        <div className="space-y-4">
          <h2 className="font-bold text-lg text-slate-800 flex items-center gap-2">
             ⚠️ Acțiuni Critice
          </h2>
          {data.urgent_actions.map(action => (
            <div key={action.id} className="bg-red-50 border border-red-100 p-4 rounded-xl flex gap-4 items-start cursor-pointer hover:bg-red-100 transition">
              <div className="bg-white p-2 rounded-full shadow-sm">
                <AlertOctagon className="w-5 h-5 text-red-500" />
              </div>
              <div>
                <h4 className="font-bold text-red-900">{action.title}</h4>
                <p className="text-red-700 text-sm mt-1">{action.desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* AI Recommendations */}
        <div className="space-y-4">
          <h2 className="font-bold text-lg text-slate-800 flex items-center gap-2">
             ✨ BizGenie Insights
          </h2>
          {data.ai_recommendations.map(rec => (
            <div key={rec.id} className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-100 p-4 rounded-xl shadow-sm">
              <div className="flex gap-3">
                <Lightbulb className="w-5 h-5 text-blue-600 shrink-0 mt-1" />
                <p className="text-blue-900 text-sm leading-relaxed font-medium">{rec.text}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
