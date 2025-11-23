import React, { useState } from 'react';
import { MOCK_RESTAURANT_DATA } from '../data/mockData';
import { Scale, CheckCircle, Clock, AlertTriangle, FileText, Download, ShieldCheck, Loader2 } from 'lucide-react';

export default function Legal() {
  const [data] = useState(MOCK_RESTAURANT_DATA.legal);
  const [isGenerating, setIsGenerating] = useState(false);

  // Simulam generarea unui document nou de catre AI
  const handleGenerateDoc = () => {
    setIsGenerating(true);
    setTimeout(() => setIsGenerating(false), 2000);
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Scale className="w-6 h-6 text-blue-600" />
            Legal & Conformitate
          </h1>
          <p className="text-slate-500">Documente gestionate de Legal Agent</p>
        </div>
        
        <button 
          onClick={handleGenerateDoc}
          disabled={isGenerating}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-xl font-medium shadow-lg shadow-slate-200 transition-all disabled:opacity-70"
        >
          {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
          {isGenerating ? 'Generare...' : 'Verifică Conformitate'}
        </button>
      </div>

      {/* Top Stats */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-6 text-white shadow-lg flex flex-col md:flex-row items-center justify-between">
        <div className="flex items-center gap-4 mb-4 md:mb-0">
          <div className="p-3 bg-white/20 rounded-full backdrop-blur-sm">
            <ShieldCheck className="w-8 h-8 text-white" />
          </div>
          <div>
            <p className="text-blue-100 text-sm font-medium">Scor Conformitate</p>
            <h2 className="text-3xl font-bold">{data.compliance_score}/100</h2>
            <p className="text-xs text-blue-200">Firma este în parametrii legali.</p>
          </div>
        </div>
        <div className="text-right">
            <p className="text-blue-200 text-sm uppercase tracking-widest font-semibold">Status Juridic</p>
            <p className="text-2xl font-bold">{data.status}</p>
            <p className="text-sm text-blue-100 opacity-80">{data.reg_number}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* COLOANA 1: Checklist (AI Workflow) */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-slate-400" />
            Pași Înființare & Autorizare
          </h3>
          
          <div className="space-y-6 relative before:absolute before:left-3.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-100">
            {data.checklist.map((step) => (
              <div key={step.id} className="relative pl-10">
                {/* Iconita status */}
                <div className={`absolute left-0 top-1 w-7 h-7 rounded-full flex items-center justify-center border-4 border-white ${
                  step.status === 'completed' ? 'bg-emerald-500 text-white' :
                  step.status === 'in_progress' ? 'bg-blue-500 text-white' :
                  'bg-slate-200 text-slate-500'
                }`}>
                  {step.status === 'completed' ? <CheckCircle className="w-3.5 h-3.5" /> :
                   step.status === 'in_progress' ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> :
                   <Clock className="w-3.5 h-3.5" />}
                </div>

                {/* Continut */}
                <div>
                  <h4 className={`font-bold ${step.status === 'pending' ? 'text-slate-500' : 'text-slate-800'}`}>
                    {step.task}
                  </h4>
                  {step.date && <p className="text-xs text-slate-400 mt-0.5">Finalizat: {step.date}</p>}
                  
                  {/* Note speciale de la Agent */}
                  {step.agent_note && (
                    <div className={`mt-2 p-2 rounded-lg text-xs font-medium ${
                      step.urgent ? 'bg-red-50 text-red-700 border border-red-100' : 'bg-blue-50 text-blue-700'
                    }`}>
                      🤖 Agent: {step.agent_note}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* COLOANA 2: Document Repository */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-slate-400" />
            Seif Documente Digitale
          </h3>

          <div className="space-y-3">
            {data.documents.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between p-3 rounded-xl border border-slate-100 hover:border-blue-200 hover:bg-blue-50/30 transition group">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-red-50 rounded-lg flex items-center justify-center shrink-0">
                    <FileText className="w-5 h-5 text-red-500" />
                  </div>
                  <div>
                    <h5 className="font-bold text-slate-700 text-sm">{doc.name}</h5>
                    <p className="text-xs text-slate-400">{doc.type} • {doc.size}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  {doc.status === 'expiring' && (
                    <span className="text-[10px] font-bold bg-amber-100 text-amber-700 px-2 py-1 rounded-full flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3" /> Expiră
                    </span>
                  )}
                  <button className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-100 rounded-lg transition-colors">
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
            
            {/* Upload Area */}
            <div className="mt-4 border-2 border-dashed border-slate-200 rounded-xl p-6 text-center hover:bg-slate-50 transition cursor-pointer">
              <p className="text-sm text-slate-500 font-medium">Trage fișiere aici pentru analiză</p>
              <p className="text-xs text-slate-400">Legal Agent va extrage automat datele.</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}