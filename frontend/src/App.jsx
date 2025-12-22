import { useState, useRef } from 'react'

function App() {
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null); // <--- NEW STATE

  const fileInputRef = useRef(null);

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // 1. Create a fake URL to show the image immediately
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);

    setAnalyzing(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Failed to analyze image");

      const data = await response.json();
      setResult(data.data);

    } catch (err) {
      console.error(err);
      setError("Something went wrong. Is the backend running?");
    } finally {
      setAnalyzing(false);
    }
  };

  // Helper to reset everything
  const resetApp = () => {
    setResult(null);
    setPreviewUrl(null);
    setAnalyzing(false);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center p-4 font-sans">

      <header className="w-full max-w-md flex justify-between items-center mb-8 pt-4">
        <h1 className="text-2xl font-bold tracking-tighter text-blue-400">
          DIAMOND<span className="text-white">MIND</span>
        </h1>
        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-xs font-bold">
          S
        </div>
      </header>

      <main className="w-full max-w-md flex-grow flex flex-col gap-6">

        {error && (
          <div className="bg-red-500/10 border border-red-500 text-red-200 p-4 rounded-xl text-sm text-center">
            {error}
          </div>
        )}

        {analyzing ? (
          <div className="bg-slate-800 rounded-2xl aspect-[3/4] flex flex-col items-center justify-center relative overflow-hidden">
            {/* Show the image dimmed while loading */}
            {previewUrl && (
              <img src={previewUrl} className="absolute inset-0 w-full h-full object-cover opacity-30 blur-sm" />
            )}
            <div className="relative z-10 flex flex-col items-center">
              <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-blue-400 font-bold">Scouting the Player...</p>
            </div>
          </div>
        ) : result ? (

          /* RESULT CARD */
          <div className="bg-slate-800 rounded-2xl overflow-hidden border border-slate-700 shadow-xl">

            {/* IMAGE HEADER (New!) */}
            <div className="relative h-64 bg-black">
              <img src={previewUrl} className="w-full h-full object-cover opacity-90" />
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-slate-900 to-transparent h-20"></div>

              {/* Score Badge floating on image */}
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
            </div>
          </div>
        )}

      </main>
    </div>
  )
}

export default App