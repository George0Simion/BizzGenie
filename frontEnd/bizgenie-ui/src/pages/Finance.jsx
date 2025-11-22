import React, { useState } from 'react';
import { MOCK_RESTAURANT_DATA } from '../data/mockData';
import { Wallet, ArrowUpRight, ArrowDownRight, FileText, Download, TrendingUp } from 'lucide-react';

export default function Finance() {
  const [data] = useState(MOCK_RESTAURANT_DATA.finance);

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Wallet className="w-6 h-6 text-emerald-600" />
            Finanțe & Plăți
          </h1>
          <p className="text-slate-500">Monitorizat de Finance Agent</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 font-medium text-sm shadow-sm transition">
          <Download className="w-4 h-4" />
          Export Raport
        </button>
      </div>

      {/* Carduri Principale */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Balanta */}
        <div className="bg-slate-900 text-white p-6 rounded-2xl shadow-lg relative overflow-hidden">
          <div className="relative z-10">
            <p className="text-slate-400 text-sm font-medium mb-1">Balanță Curentă</p>
            <h2 className="text-3xl font-bold">{data.current_balance}</h2>
            <div className="mt-4 inline-flex items-center gap-1 px-2 py-1 bg-white/10 rounded-lg text-xs text-emerald-300">
              <TrendingUp className="w-3 h-3" /> +12% vs luna trecută
            </div>
          </div>
          {/* Decor */}
          <div className="absolute right-0 top-0 w-32 h-32 bg-white/5 rounded-full -mr-10 -mt-10 blur-2xl"></div>
        </div>

        {/* Cheltuieli */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
           <div className="flex justify-between items-start">
              <div>
                <p className="text-slate-500 text-sm font-medium">Cheltuieli (Luna asta)</p>
                <h2 className="text-2xl font-bold text-slate-800 mt-1">{data.expenses_this_month}</h2>
              </div>
              <div className="p-2 bg-red-50 rounded-lg"><ArrowDownRight className="w-6 h-6 text-red-500" /></div>
           </div>
           <div className="w-full bg-slate-100 h-2 mt-4 rounded-full overflow-hidden">
             <div className="bg-red-500 h-full w-[65%] rounded-full"></div>
           </div>
           <p className="text-xs text-slate-400 mt-2">65% din buget consumat</p>
        </div>

        {/* Profit */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
           <div className="flex justify-between items-start">
              <div>
                <p className="text-slate-500 text-sm font-medium">Marjă Profit</p>
                <h2 className="text-2xl font-bold text-slate-800 mt-1">{data.profit_margin}</h2>
              </div>
              <div className="p-2 bg-emerald-50 rounded-lg"><ArrowUpRight className="w-6 h-6 text-emerald-500" /></div>
           </div>
           <div className="mt-4 flex items-end gap-1 h-10">
             {/* Mini grafic din bare CSS */}
             {data.monthly_revenue.map((val, i) => (
                <div key={i} className="flex-1 bg-emerald-100 rounded-t-sm hover:bg-emerald-200 transition-colors relative group">
                  <div 
                    className="absolute bottom-0 w-full bg-emerald-500 rounded-t-sm transition-all duration-500" 
                    style={{ height: `${(val / 8000) * 100}%` }}
                  ></div>
                  {/* Tooltip */}
                  <div className="opacity-0 group-hover:opacity-100 absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[10px] px-2 py-1 rounded pointer-events-none transition-opacity">
                    {val}
                  </div>
                </div>
             ))}
           </div>
        </div>
      </div>

      {/* Tabel Tranzactii */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100">
          <h3 className="font-bold text-slate-800">Tranzacții Recente</h3>
        </div>
        <div className="divide-y divide-slate-100">
          {data.recent_transactions.map((tx) => (
            <div key={tx.id} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-full ${
                  tx.type === 'income' ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-100 text-slate-600'
                }`}>
                  {tx.type === 'income' ? <ArrowUpRight className="w-5 h-5" /> : <FileText className="w-5 h-5" />}
                </div>
                <div>
                  <p className="font-bold text-slate-800">{tx.to}</p>
                  <p className="text-xs text-slate-500">{tx.date} • {tx.status === 'pending' ? 'În procesare' : 'Complet'}</p>
                </div>
              </div>
              <div className="text-right">
                <p className={`font-bold ${tx.type === 'income' ? 'text-emerald-600' : 'text-slate-800'}`}>
                  {tx.amount}
                </p>
                {tx.status === 'pending' && (
                  <span className="text-[10px] bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-bold">Pending</span>
                )}
              </div>
            </div>
          ))}
        </div>
        <div className="p-4 border-t border-slate-100 bg-slate-50 text-center">
          <button className="text-sm text-blue-600 font-medium hover:underline">Vezi tot istoricul</button>
        </div>
      </div>
    </div>
  );
}