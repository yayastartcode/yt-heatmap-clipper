import { Link, useLocation } from 'react-router-dom';

export default function Layout({ children }) {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen flex flex-col bg-slate-900">
      <nav className="bg-slate-800/50 backdrop-blur border-b border-slate-700/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="text-2xl font-bold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
              YT Heatmap Clipper
            </Link>
            <div className="flex gap-6">
              <Link 
                to="/" 
                className={`hover:text-blue-400 transition-colors ${isActive('/') ? 'text-blue-400' : 'text-slate-400'}`}
              >
                Home
              </Link>
              <Link 
                to="/history" 
                className={`hover:text-blue-400 transition-colors ${isActive('/history') ? 'text-blue-400' : 'text-slate-400'}`}
              >
                History
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="flex-1 container mx-auto px-4 py-8">
        {children}
      </main>

      <footer className="bg-slate-800/50 backdrop-blur border-t border-slate-700/50 py-6">
        <div className="container mx-auto px-4 text-center text-slate-400 text-sm">
          <p>YT Heatmap Clipper - Extract viral moments from YouTube videos</p>
        </div>
      </footer>
    </div>
  );
}
