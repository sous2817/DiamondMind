import { useState, useRef, useEffect } from 'react'

function App() {
  const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [history, setHistory] = useState([]);
  
  // --- NEW: State for Player Level ---
  const [level, setLevel] = useState("14u"); 

  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_URL}/history`);
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.error("Failed to load history:", err);
    }
  };

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);

    setAnalyzing(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    
    // --- NEW: Send the selected level to the backend ---
    formData.append("level", level); 

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Failed to analyze image");

      const data = await response.json();
      setResult(data.data);
      fetchHistory();
      
    } catch (err) {
      console.error(err);
      setError("Something went wrong. Is the backend running?");
    } finally {
      setAnalyzing(false);
    }
  };

  const resetApp = () => {
    setResult(null);
    setPreviewUrl(null);
    setAnalyzing(false);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center p-4 font-sans">
      
      <header className="w-full max-w-md flex justify-between items-center mb-6 pt-4">
        <h1 className="text-2xl font-bold tracking-tighter text-blue-400">
          DIAMOND<span className="text-white">MIND</span>
        </h1>
        
        {/* --- NEW: Level Selector (Top Right) --- */}
        <select 
          value={level} 
          onChange={(e) => setLevel(e.target.value)}
          className="bg-slate-800 text-white text-xs font-bold py-1 px-3 rounded-full border border-slate-600 focus:outline-none focus:border-blue-500"
        >
          <option value="10u">🦁 10U (Fun)</option>
          <option value="14u">⚾ 14U (Std)</option>
          <option value="varsity">🎓 Varsity (Pro)</option>
        </select>
      </header>

      <main className="w-full max-w-md flex-grow flex flex-col gap-6">
        
        {error && (
          <div className="bg-red-500/10 border border-red-500 text-red-200 p-4 rounded-xl text-sm text-center">
            {error}
          </div>
        )}

        {analyzing ? (
          <div className="bg-slate-800 rounded-2xl aspect-[3/4] flex flex-col items-center justify-center relative overflow-hidden">
            {previewUrl && (
              <img src={previewUrl} className="absolute inset-0 w-full h-full object-cover opacity-30 blur-sm" />
            )}
            <div className="relative z-10 flex flex-col items-center">
              <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-blue-400 font-bold">Scouting the Player...</p>
              {/* Show which coach is analyzing */}
              <p className="text-slate-500 text-xs mt-1 uppercase tracking-widest">
                {level === '10u' ? 'Little League Coach' : level === 'varsity' ? 'Pro Scout' : 'Travel Coach'}
              </p>
            </div>
          </div>
        ) : result ? (
          
          /* RESULT CARD */
          <div className="bg-slate-800 rounded-2xl overflow-hidden border border-slate-700 shadow-xl">
            <div className="relative h-64 bg-black">
              <img src={previewUrl} className="w-full h-full object-cover opacity-90" />
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-slate-900 to-transparent h-20"></div>
              <div className="absolute bottom-4 right-4 bg-slate-900/90 backdrop-blur px-4 py-2 rounded-xl border border-slate-700 flex flex-col items-center">
                <span className={`text-3xl font-black ${result.score >= 7 ? 'text-green-400' : result.score >= 4 ? 'text-yellow-400' : 'text-red-400'}`}>
                  {result.score}
                </span>
                <span className="text-[10px] text-slate-400 uppercase font-bold">Score</span>
              </div>
            </div>

            <div className="p-6">
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-white">{result.phase}</h2>
                <p className="text-slate-400 text-sm">Phase Detected</p>
              </div>

              <div className="space-y-4 mb-6">
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Coach's Feedback</h3>
                <ul className="space-y-3">
                  {result.feedback.map((item, index) => (
                    <li key={index} className="flex gap-3 text-sm text-slate-300 bg-slate-700/30 p-3 rounded-lg border border-slate-700/50">
                      <span className="text-blue-400 mt-0.5">•</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-blue-600/10 border border-blue-500/20 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xl">⚾</span>
                  <h3 className="font-bold text-blue-100">Drill: {result.drill}</h3>
                </div>
                <p className="text-sm text-blue-200/80 leading-relaxed">
                  {result.drill_explanation}
                </p>
              </div>

              <button 
                onClick={resetApp}
                className="w-full mt-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition-colors"
              >
                Analyze Another Swing
              </button>
            </div>
          </div>

        ) : (
          
          /* UPLOAD CARD */
          <div 
            onClick={() => fileInputRef.current.click()} 
            className="bg-slate-800 rounded-2xl aspect-[3/4] border-2 border-dashed border-slate-600 flex flex-col items-center justify-center relative overflow-hidden group hover:border-blue-500 transition-colors cursor-pointer"
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileSelect} 
              className="hidden" 
              accept="image/*"
            />
            <div className="text-center p-6 pointer-events-none">
              <div className="w-16 h-16 bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-blue-600 transition-colors shadow-lg">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8 text-white">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0ZM18.75 10.5h.008v.008h-.008V10.5Z" />
                </svg>
              </div>
              <p className="text-slate-300 font-medium text-lg">Tap to Analyze</p>
              
              {/* --- NEW: Dynamic Hint --- */}
               <p className="text-slate-500 text-sm mt-2">
                 {level === '10u' ? "Show me your swing, kiddo! 🦁" : level === 'varsity' ? "Upload mechanics for review." : "Upload Photo of Swing"}
               </p>

            </div>
          </div>
        )}

        {/* HISTORY LIST (Unchanged) */}
        {history.length > 0 && (
          <div className="mt-8">
            <h3 className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-4 px-1">Recent Sessions</h3>
            <div className="space-y-3">
              {history.map((item) => (
                <div key={item.id} className="bg-slate-800 p-3 rounded-xl flex items-center justify-between border border-slate-700">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center text-xl">
                      {item.score >= 7 ? '🔥' : '⚠️'}
                    </div>
                    <div>
                      <p className="font-bold text-sm text-slate-200">{item.phase}</p>
                      <p className="text-[10px] text-slate-400 font-mono mt-0.5">
                        {new Date(item.created_at).toLocaleDateString()} • {new Date(item.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                      </p>
                    </div>
                  </div>
                  <div className={`font-black text-lg ${item.score >= 7 ? 'text-green-400' : item.score >= 4 ? 'text-yellow-400' : 'text-red-400'}`}>
                    {item.score}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </main>
    </div>
  )
}

export default App