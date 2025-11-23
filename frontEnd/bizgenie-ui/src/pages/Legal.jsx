import React, { useState } from 'react';
import { useBusiness } from '../context/BusinessContext';
import { Scale, ChevronDown, ChevronUp, CheckCircle, Clock, Loader2, Square, CheckSquare, Save, Trash2 } from 'lucide-react';

export default function Legal() {
  const { legalTasks = [], toggleLegalStep, saveLegalChanges, deleteLegalTask } = useBusiness() || {};
  const [expandedId, setExpandedId] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const toggleExpand = (id) => {
    if (expandedId === id) {
      setExpandedId(null);
    } else {
      setExpandedId(id);
    }
  };

  const handleSave = async () => {
      if (!saveLegalChanges) {
          alert("Eroare: Funcția de salvare nu este disponibilă.");
          return;
      }
      setIsSaving(true);
      try {
        await saveLegalChanges();
      } catch (error) {
        console.error("Eroare la salvare:", error);
        alert("Nu s-a putut salva. Verifică conexiunea cu serverul.");
      } finally {
        setTimeout(() => setIsSaving(false), 1000);
      }
  };

  const handleDelete = (e, id) => {
      e.stopPropagation(); 
      if (confirm("Ești sigur că vrei să elimini acest task?")) {
          deleteLegalTask(id);
      }
  }

  const getStatusIcon = (status) => {
    if (status === 'completed') return <CheckCircle className="w-5 h-5 text-emerald-500" />;
    if (status === 'in_progress') return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
    // Default pentru pending
    return <Clock className="w-5 h-5 text-slate-400" />;
  };

  if (!Array.isArray(legalTasks)) {
      return <div className="p-10 text-center text-slate-500">Se încarcă datele legale...</div>;
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      
      {/* HEADER */}
      <div className="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
            <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <Scale className="text-blue-600" />
            Monitorizare Legală & Birocrație
            </h1>
            <p className="text-slate-500">Bifează pașii finalizați și salvează pentru a anunța echipa.</p>
        </div>

        <button 
            onClick={handleSave}
            disabled={isSaving}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-white shadow-lg transition-all transform active:scale-95 ${
                isSaving ? 'bg-slate-400 cursor-wait' : 'bg-blue-600 hover:bg-blue-700 hover:shadow-blue-200'
            }`}
        >
            {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            {isSaving ? 'Se salvează...' : 'Salvează Modificările'}
        </button>
      </div>

      <div className="space-y-4">
        {legalTasks.length === 0 && (
            <div className="text-center p-10 text-slate-400 bg-white rounded-xl border border-slate-200">
                Nu există task-uri legale momentan.
            </div>
        )}

        {legalTasks.map((task) => (
          <div 
            key={task.id} 
            className={`bg-white rounded-xl border transition-all duration-300 overflow-hidden ${
              expandedId === task.id ? 'border-blue-500 shadow-md' : 'border-slate-200 hover:border-blue-300'
            }`}
          >
            {/* HEADER TASK */}
            <div 
              onClick={() => toggleExpand(task.id)}
              className="p-5 flex items-center justify-between cursor-pointer bg-white select-none group"
            >
              <div className="flex items-center gap-4">
                <div className="p-2 bg-slate-50 rounded-full">
                    {getStatusIcon(task.status)}
                </div>
                <div>
                  <h3 className="font-bold text-slate-800 text-lg">{task.title}</h3>
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold mt-1">
                    Status: <span className={
                        task.status === 'completed' ? 'text-emerald-600' : 
                        task.status === 'in_progress' ? 'text-blue-600' : 'text-slate-500'
                    }>{(task.status || 'pending').replace('_', ' ')}</span>
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                {/* BUTON DELETE - Apare ORICAND (la hover) */}
                <button 
                    onClick={(e) => handleDelete(e, task.id)}
                    className="p-2 text-slate-300 hover:text-red-600 hover:bg-red-50 rounded-full transition-all opacity-0 group-hover:opacity-100"
                    title="Elimină Task"
                >
                    <Trash2 className="w-5 h-5" />
                </button>
                
                <div className="text-slate-400">
                    {expandedId === task.id ? <ChevronUp /> : <ChevronDown />}
                </div>
              </div>
            </div>

            {/* BODY TASK */}
            {expandedId === task.id && (
              <div className="px-5 pb-5 pt-0 bg-white animate-in slide-in-from-top-2 duration-200">
                <div className="pl-14">
                  
                  <div className="p-3 bg-blue-50 rounded-lg text-blue-800 text-sm mb-4 leading-relaxed border border-blue-100">
                    <strong>Descriere Agent:</strong> {task.description || "Fără descriere."}
                  </div>

                  <h4 className="font-bold text-slate-700 mb-3 text-sm">Pași de urmat:</h4>
                  <div className="space-y-2">
                    {task.steps && Array.isArray(task.steps) ? (
                        task.steps.map((step, index) => (
                        <div 
                            key={index} 
                            onClick={() => toggleLegalStep && toggleLegalStep(task.id, step.step)} 
                            className="flex items-center gap-3 p-2 hover:bg-slate-50 rounded-lg transition-colors cursor-pointer group"
                        >
                            {step.done ? (
                            <CheckSquare className="w-5 h-5 text-emerald-500 shrink-0 transition-all" />
                            ) : (
                            <Square className="w-5 h-5 text-slate-300 group-hover:text-blue-400 shrink-0 transition-all" />
                            )}
                            
                            <span className={`text-sm select-none ${step.done ? 'text-slate-400 line-through decoration-slate-300' : 'text-slate-700'}`}>
                            {step.step}
                            </span>
                        </div>
                        ))
                    ) : (
                        <p className="text-sm text-slate-400 italic">Nu există pași definiți.</p>
                    )}
                  </div>

                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}