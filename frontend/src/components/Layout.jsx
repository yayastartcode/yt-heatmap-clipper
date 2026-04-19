import { Link, useLocation } from 'react-router-dom';

export default function Layout({ children }) {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-dark-card border-b border-dark-border">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="text-2xl font-bold bg-gradient-to-r from-accent-blue to-accent-purple bg-clip-text text-transparent">
              YT Heatmap Clipper
            </Link>
            <div className="flex gap-6">
              <Link 
                to="/" 
                className={`hover:text-accent-blue transition ${isActive('/') ? 'text-accent-blue' : 'text-gray-400'}`}
              >
                Home
              </Link>
              <Link 
                to="/history" 
                className={`hover:text-accent-blue transition ${isActive('/history') ? 'text-accent-blue' : 'text-gray-400'}`}
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

      <footer className="bg-dark-card border-t border-dark-border py-6">
        <div className="container mx-auto px-4 text-center text-gray-400 text-sm">
          <p>YT Heatmap Clipper - Extract viral moments from YouTube videos</p>
        </div>
      </footer>
    </div>
  );
}
