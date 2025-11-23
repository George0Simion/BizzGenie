import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, Loader2, AlertCircle, Download } from 'lucide-react';
import { BusinessService } from '../services/api';

export default function Documents() {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = () => { setIsDragging(false); };
  const handleDrop = (e) => {
    e.preventDefault(); setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) handleFiles(e.dataTransfer.files);
  };
  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files.length > 0) handleFiles(e.target.files);
  };

  const handleFiles = async (fileList) => {
    setIsUploading(true);
    const newFiles = Array.from(fileList).map(file => ({
      file, name: file.name, size: (file.size / 1024 / 1024).toFixed(2) + ' MB', status: 'uploading'
    }));

    setFiles(prev => [...newFiles, ...prev]);

    for (let fileObj of newFiles) {
      try {
        const formData = new FormData();
        formData.append('file', fileObj.file);
        await BusinessService.uploadDocument(formData);
        setFiles(prev => prev.map(f => f.name === fileObj.name ? { ...f, status: 'success' } : f));
      } catch (error) {
        setFiles(prev => prev.map(f => f.name === fileObj.name ? { ...f, status: 'error' } : f));
      }
    }
    setIsUploading(false);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <FileText className="text-blue-600" /> Documente & Facturi
        </h1>
        <p className="text-slate-500">Încarcă documente pentru analiză.</p>
      </div>

      <div 
        className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all cursor-pointer ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50'}`}
        onDragOver={handleDragOver} onDragLeave={handleDragLeave} onDrop={handleDrop}
        onClick={() => document.getElementById('fileInput').click()}
      >
        <input type="file" id="fileInput" className="hidden" multiple onChange={handleFileSelect} />
        <div className="flex flex-col items-center justify-center gap-4">
          <div className={`p-4 rounded-full ${isDragging ? 'bg-blue-100 text-blue-600' : 'bg-slate-100 text-slate-400'}`}><Upload className="w-8 h-8" /></div>
          <div>
            <p className="text-lg font-bold text-slate-700">{isDragging ? "Eliberează" : "Trage fișiere sau click"}</p>
            <p className="text-sm text-slate-400 mt-1">PDF, JPG, PNG, Excel</p>
          </div>
        </div>
      </div>

      {files.length > 0 && (
        <div className="mt-8">
          <h3 className="font-bold text-slate-800 mb-4">Fișiere Recente</h3>
          <div className="space-y-3">
            {files.map((file, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 bg-white border border-slate-100 rounded-xl shadow-sm">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-blue-50 rounded-lg"><FileText className="w-6 h-6 text-blue-600" /></div>
                  <div>
                    <p className="font-bold text-slate-700 text-sm">{file.name}</p>
                    <p className="text-xs text-slate-400">{file.size}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {file.status === 'uploading' && <span className="flex items-center gap-2 text-blue-600 text-xs font-bold bg-blue-50 px-3 py-1 rounded-full"><Loader2 className="w-3 h-3 animate-spin" /> Se încarcă...</span>}
                  {file.status === 'success' && (
                      <div className="flex items-center gap-3">
                        <span className="flex items-center gap-2 text-emerald-600 text-xs font-bold bg-emerald-50 px-3 py-1 rounded-full"><CheckCircle className="w-3 h-3" /> Analizat</span>
                        
                        {/* BUTON DOWNLOAD */}
                        <a href={`http://localhost:5000/api/files/${file.name}`} target="_blank" rel="noreferrer" className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors" title="Descarcă">
                            <Download className="w-5 h-5" />
                        </a>
                      </div>
                  )}
                  {file.status === 'error' && <span className="flex items-center gap-2 text-red-600 text-xs font-bold bg-red-50 px-3 py-1 rounded-full"><AlertCircle className="w-3 h-3" /> Eroare</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}