import React from 'react';
import { LayoutDashboard } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full text-center border border-slate-100">
        <div className="flex justify-center mb-4">
          <div className="bg-blue-100 p-4 rounded-full">
            <LayoutDashboard className="w-10 h-10 text-blue-600" />
          </div>
        </div>
        <h1 className="text-3xl font-bold text-slate-800 mb-2">BizGenie UI 🧞‍♂️</h1>
        <p className="text-slate-500 mb-6">
          Sistemul este pregătit. Tailwind și React funcționează!
        </p>
        <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-xl transition-all w-full">
          Începe Dashboard-ul
        </button>
      </div>
    </div>
  );
}

export default App;