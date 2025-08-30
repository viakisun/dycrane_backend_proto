import React from 'react';
import { Routes, Route, Link, NavLink } from 'react-router-dom';
import Particles from './components/Particles';
import HomePage from './pages/HomePage';
import OwnersListPage from './pages/OwnersListPage';
import TestClientPage from './pages/TestClientPage';
import CranesListPage from './pages/CranesListPage';
import RequestsListPage from './pages/RequestsListPage';
import CraneModelSearchPage from './pages/CraneModelSearchPage';
import './components/Particles.css';

const App: React.FC = () => {
  const navLinkClasses = ({ isActive }: { isActive: boolean }) =>
    `px-4 py-2 rounded-md text-sm font-medium transition-all duration-300
    ${isActive
      ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/30'
      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
    }`;

  return (
    <div className="min-h-screen flex flex-col">
      <Particles />
      <header className="bg-black bg-opacity-30 border-b border-cyan-glow/20 backdrop-blur-sm sticky top-0 z-40">
        <nav className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="text-2xl font-bold text-cyan-glow uppercase" style={{ textShadow: '0 0 8px #00ffff' }}>
              DY-Crane
            </Link>
            <div className="flex items-center space-x-4">
              <NavLink to="/" className={navLinkClasses}>
                Dashboard
              </NavLink>
              <NavLink to="/owners" className={navLinkClasses}>
                Owners
              </NavLink>
              <NavLink to="/sites" className={navLinkClasses}>
                Sites
              </NavLink>
              <NavLink to="/crane-models" className={navLinkClasses}>
                Crane Models
              </NavLink>
              <NavLink to="/requests" className={navLinkClasses}>
                Requests
              </NavLink>
               <NavLink to="/test-client" className={navLinkClasses}>
                E2E Test Client
              </NavLink>
            </div>
          </div>
        </nav>
      </header>

      <main className="flex-grow container mx-auto p-4 sm:p-6 lg:p-8">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/owners" element={<OwnersListPage />} />
          <Route path="/owners/:ownerId/cranes" element={<CranesListPage />} />
          <Route path="/requests" element={<RequestsListPage />} />
          <Route path="/crane-models" element={<CraneModelSearchPage />} />
          <Route path="/test-client" element={<TestClientPage />} />
          {/* Add other routes here as pages are created */}
        </Routes>
      </main>
    </div>
  );
};

export default App;
