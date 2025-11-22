import React, { useState } from 'react';
import { Rocket, Building2, Send, Loader2, Upload } from 'lucide-react';
import { useBusiness } from '../context/BusinessContext';

export default function Onboarding() {
  const { startNewBusiness, connectExistingBusiness, isLoading } = useBusiness();
  const [mode, setMode] = useState('select'); // 'select', 'new', 'existing'
  const [input, setInput] = useState('');
  
  // State pentru formularul existent
  const [formData, setFormData] = useState({ name: '', cui: '' });

  // Functia pentru Business Nou (Chat Style)
  const handleNewBusinessSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    startNewBusiness(input);
  };

  // Functia pentru Business Existent
  const handleExistingSubmit = (e) => {
    e.preventDefault();
    connectExistingBusiness(formData);
  };

  if (isLoading) {
    return (
      <div className="h-screen flex flex-col items-center justify-center bg-slate-50">
        <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
        <h2 className="text-xl font-bold text-slate-700">BizGenie AI analizează datele...</h2>
        <p className="text-slate-500">Configurăm dashboard-ul personalizat.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-4xl w-full flex flex-col md:flex-row overflow-hidden min-h-[500px]">
        
        {/* Left Side - Hero */}
        <div className="md:w-1/2 pr-0 md:pr-8 flex flex-col justify-center border-b md:border-b-0 md:border-r border-slate-100 pb-8 md:pb-0">
          <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center mb-6">
            <Rocket className="text-white w-6 h-6" />
          </div>
          <h1 className="text-3xl font-bold text-slate-800 mb-4">Salut! Sunt BizGenie.</h1>
          <p className="text-slate-600 text-lg leading-relaxed">
            Co-pilotul tău AI pentru afaceri. Eu mă ocup de birocrație, stocuri și legal, ca tu să te ocupi de pasiune.
          </p>
        </div>

        {/* Right Side - Interaction */}
        <div className="md:w-1/2 pl-0 md:pl-8 pt-8 md:pt-0 flex flex-col justify-center">
          
          {/* 1. SELECT MODE */}
          {mode === 'select' && (
            <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-500">
              <p className="text-slate-500 font-medium mb-2">Cum vrei să începem?</p>
              
              <button 
                onClick={() => setMode('new')}
                className="w-full p-4 border-2 border-blue-100 hover:border-blue-500 hover:bg-blue-50 rounded-xl flex items-center gap-4 transition-all group text-left"
              >
                <div className="bg-blue-100 p-3 rounded-lg group-hover:bg-blue-500 transition-colors">
                  <Rocket className="w-6 h-6 text-blue-600 group-hover:text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-800">Vreau să încep un business</h3>
                  <p className="text-xs text-slate-500">Discută cu AI-ul pentru a genera planul.</p>
                </div>
              </button>

              <button 
                onClick={() => setMode('existing')}
                className="w-full p-4 border-2 border-slate-100 hover:border-slate-400 hover:bg-slate-50 rounded-xl flex items-center gap-4 transition-all group text-left"
              >
                <div className="bg-slate-100 p-3 rounded-lg group-hover:bg-slate-600 transition-colors">
                  <Building2 className="w-6 h-6 text-slate-600 group-hover:text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-800">Am deja o afacere</h3>
                  <p className="text-xs text-slate-500">Conectează datele și lasă AI-ul să ajute.</p>
                </div>
              </button>
            </div>
          )}

          {/* 2. NEW BUSINESS MODE (Chat simplificat) */}
          {mode === 'new' && (
            <div className="animate-in fade-in slide-in-from-right-4 duration-500">
              <h3 className="font-bold text-xl mb-2">Descrie-mi ideea ta</h3>
              <p className="text-sm text-slate-500 mb-4">Ex: "Vreau să deschid o pizzerie în București cu livrare."</p>
              
              <form onSubmit={handleNewBusinessSubmit}>
                <textarea 
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  className="w-full h-32 p-4 bg-slate-50 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none mb-4"
                  placeholder="Scrie aici..."
                />
                <div className="flex gap-2">
                  <button type="button" onClick={() => setMode('select')} className="px-4 py-2 text-slate-500 hover:text-slate-800">
                    Înapoi
                  </button>
                  <button type="submit" className="flex-1 bg-blue-600 text-white rounded-xl py-2 font-bold hover:bg-blue-700 transition flex items-center justify-center gap-2">
                    <Send className="w-4 h-4" /> Analizează Ideea
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* 3. EXISTING BUSINESS MODE (Form) */}
          {mode === 'existing' && (
            <div className="animate-in fade-in slide-in-from-right-4 duration-500">
              <h3 className="font-bold text-xl mb-2">Detalii Afacere</h3>
              <form onSubmit={handleExistingSubmit} className="space-y-4">
                <div>
                  <label className="text-xs font-bold text-slate-500 uppercase">Nume Firmă</label>
                  <input 
                    type="text" 
                    value={formData.name}
                    onChange={e => setFormData({...formData, name: e.target.value})}
                    className="w-full p-3 bg-slate-50 rounded-lg border border-slate-200 focus:outline-none focus:border-blue-500"
                    placeholder="Ex: Fresh Start Cafe SRL"
                    required
                  />
                </div>
                <div>
                  <label className="text-xs font-bold text-slate-500 uppercase">CUI (Opțional)</label>
                  <input 
                    type="text" 
                    value={formData.cui}
                    onChange={e => setFormData({...formData, cui: e.target.value})}
                    className="w-full p-3 bg-slate-50 rounded-lg border border-slate-200 focus:outline-none focus:border-blue-500"
                    placeholder="RO..."
                  />
                </div>
                
                <div className="p-4 border-2 border-dashed border-slate-200 rounded-xl text-center cursor-pointer hover:bg-slate-50">
                  <Upload className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                  <p className="text-sm text-slate-500">Încarcă documente (opțional)</p>
                  <p className="text-xs text-slate-400">PDF, Excel</p>
                </div>

                <div className="flex gap-2 pt-2">
                  <button type="button" onClick={() => setMode('select')} className="px-4 py-2 text-slate-500 hover:text-slate-800">
                    Înapoi
                  </button>
                  <button type="submit" className="flex-1 bg-slate-800 text-white rounded-xl py-2 font-bold hover:bg-slate-900 transition">
                    Intră în Dashboard
                  </button>
                </div>
              </form>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}