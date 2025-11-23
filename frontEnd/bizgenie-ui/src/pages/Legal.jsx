import React, { useState, useEffect } from 'react';
import { useBusiness } from '../context/BusinessContext';
import { Scale, ChevronDown, ChevronUp, CheckCircle, Clock, Loader2, Square, CheckSquare, Save, Trash2, ExternalLink, AlertTriangle, BookOpen, Shield } from 'lucide-react';

export default function Legal() {
  const { legalTasks, toggleLegalStep, saveLegalChanges, deleteLegalTask } = useBusiness() || {};
  const [expandedId, setExpandedId] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  
  // --- STARE PENTRU TIMEOUT ---
  const [isTimeout, setIsTimeout] = useState(false);

  useEffect(() => {
    // --- SCHIMBARE AICI: 5 SECUNDE ---
    // Dupa 5 secunde, oprim loading-ul fortat si aratam lista goala daca nu au venit date
    const timer = setTimeout(() => {
        setIsTimeout(true);
    }, 5000);

    // Curatam timerul daca plecam de pe pagina
    return () => clearTimeout(timer);
  }, []);

  const toggleExpand = (id) => setExpandedId(expandedId === id ? null : id);

  const handleSave = async () => {
      if (!saveLegalChanges) return;
      setIsSaving(true);
      try { await saveLegalChanges(); } catch (e) { alert("Eroare salvare."); } finally { setTimeout(() => setIsSaving(false), 1000); }
  };

  const handleDelete = (e, id) => {
      e.stopPropagation(); 
      if (confirm("Ești sigur că vrei să elimini acest task?")) deleteLegalTask(id);
  }

  const getStatusIcon = (status) => {
    if (status === 'completed') return <CheckCircle className="w-5 h-5 text-emerald-500" />;
    if (status === 'in_progress') return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
    return <Clock className="w-5 h-5 text-slate-400" />;
  };

  // --- LOGICA DE AFIȘARE ---
  // Daca datele sunt NULL si NU a trecut timpul (5s) -> Aratam Loading
  if (legalTasks === null && !isTimeout) {
      return (
        <div className="flex flex-col items-center justify-center h-[80vh] text-center p-6 animate-in fade-in duration-700">
            <div className="relative mb-6">
                <Shield className="w-16 h-16 text-slate-200" />
                <div className="absolute -bottom-2 -right-2 bg-white rounded-full p-1">
                    <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                </div>
            </div>
            <h2 className="text-2xl font-bold text-slate-800 mb-2">Analizăm conformitatea legală...</h2>
            <p className="text-slate-500 max-w-md">
                Legal Agent verifică legislația și documentele necesare.
            </p>
        </div>
      );
  }

  // Daca datele sunt inca NULL dar a trecut timpul -> Le tratam ca array gol []
  // Astfel va intra pe ramura care afiseaza "Nu sunt task-uri active"
  const safeTasks = legalTasks || [];

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-8 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
            <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Scale className="text-blue-600" /> Monitorizare Legală
            </h1>
            <p className="text-slate-500">Agentul analizează automat legislația.</p>
        </div>
        <button onClick={handleSave} disabled={isSaving} className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-white shadow-lg transition-all active:scale-95 ${isSaving ? 'bg-slate-400' : 'bg-blue-600 hover:bg-blue-700'}`}>
            {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            {isSaving ? 'Se salvează...' : 'Salvează Modificările'}
        </button>
      </div>

      <div className="space-y-4">
        {/* Mesaj cand lista e goala (sau dupa timeout) */}
        {safeTasks.length === 0 && (
            <div className="text-center p-12 bg-white rounded-xl border border-slate-200 text-slate-400 animate-in fade-in zoom-in duration-500">
                <Scale className="w-12 h-12 mx-auto mb-2 text-slate-200" />
                <h3 className="text-lg font-bold text-slate-600">Totul este în ordine.</h3>
                <p>Nu am găsit task-uri active sau serverul încă procesează.</p>
                <p className="text-xs mt-2 text-blue-400 animate-pulse">Ascultăm în continuare după schimbări...</p>
            </div>
        )}

        {safeTasks.map((task) => (
          <div key={task.id} className={`bg-white rounded-xl border transition-all duration-300 overflow-hidden ${expandedId === task.id ? 'border-blue-500 shadow-md' : 'border-slate-200 hover:border-blue-300'}`}>
            
            {/* HEADER */}
            <div onClick={() => toggleExpand(task.id)} className="p-5 flex items-center justify-between cursor-pointer bg-white select-none group">
              <div className="flex items-center gap-4">
                <div className="p-2 bg-slate-50 rounded-full">{getStatusIcon(task.status)}</div>
                <div>
                  <h3 className="font-bold text-slate-800 text-lg">{task.title}</h3>
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mt-1">
                    Status: <span className={task.status === 'completed' ? 'text-emerald-600' : task.status === 'in_progress' ? 'text-blue-600' : 'text-slate-500'}>{(task.status || 'pending').replace('_', ' ')}</span>
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <button onClick={(e) => handleDelete(e, task.id)} className="p-2 text-slate-300 hover:text-red-600 hover:bg-red-50 rounded-full transition-all opacity-0 group-hover:opacity-100"><Trash2 className="w-5 h-5" /></button>
                <div className="text-slate-400">{expandedId === task.id ? <ChevronUp /> : <ChevronDown />}</div>
              </div>
            </div>

            {/* BODY */}
            {expandedId === task.id && (
              <div className="px-5 pb-5 pt-0 bg-white animate-in slide-in-from-top-2 duration-200">
                <div className="pl-14 space-y-6">
                  
                  {/* Descriere */}
                  <div className="p-4 bg-blue-50 rounded-xl text-blue-900 text-sm leading-relaxed border border-blue-100">
                    <div className="flex items-center gap-2 mb-2 font-bold text-blue-700">
                        <BookOpen className="w-4 h-4" /> Rezumat Legislativ:
                    </div>
                    {task.description || "Fără descriere."}
                  </div>

                  {/* CHECKLIST */}
                  <div>
                    <h4 className="font-bold text-slate-800 mb-3 text-sm uppercase tracking-wide">Plan de Acțiune:</h4>
                    <div className="space-y-3">
                        {task.steps && task.steps.map((step, index) => (
                        <div key={index} onClick={() => toggleLegalStep && toggleLegalStep(task.id, step.step)} className="flex items-start gap-3 p-3 bg-slate-50 hover:bg-white border border-slate-100 hover:border-blue-200 rounded-xl transition-all cursor-pointer group shadow-sm">
                            <div className="mt-0.5">
                                {step.done ? <CheckSquare className="w-5 h-5 text-emerald-500 shrink-0" /> : <Square className="w-5 h-5 text-slate-400 group-hover:text-blue-500 shrink-0" />}
                            </div>
                            <div className="flex-1">
                                <div className={`font-medium text-sm ${step.done ? 'text-slate-500 line-through' : 'text-slate-800'}`}>{step.step}</div>
                                {step.action && <div className="text-xs text-slate-500 mt-1">{step.action}</div>}
                                
                                {/* Metadata: Citation & Link */}
                                {(step.citation || step.source) && (
                                    <div className="flex flex-wrap items-center gap-2 mt-2">
                                        {step.citation && <span className="px-2 py-0.5 bg-slate-200 text-slate-600 text-[10px] font-bold rounded uppercase tracking-wide">{step.citation}</span>}
                                        {step.source && (
                                            <a href={step.source} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()} className="flex items-center gap-1 text-[10px] text-blue-600 hover:underline font-medium">Sursă Oficială <ExternalLink className="w-3 h-3" /></a>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                        ))}
                    </div>
                  </div>

                  {/* RISKS */}
                  {task.risks && task.risks.length > 0 && (
                      <div className="border-t border-slate-100 pt-4">
                          <h4 className="font-bold text-red-800 mb-3 text-sm uppercase tracking-wide flex items-center gap-2"><AlertTriangle className="w-4 h-4" /> Riscuri Identificate:</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                              {task.risks.map((risk, i) => (
                                  <div key={i} className="p-3 bg-red-50 border border-red-100 rounded-lg text-xs">
                                      <div className="font-bold text-red-700 mb-1">{risk.risk}</div>
                                      <div className="text-red-600 opacity-80">Mitigare: {risk.mitigation}</div>
                                  </div>
                              ))}
                          </div>
                      </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}