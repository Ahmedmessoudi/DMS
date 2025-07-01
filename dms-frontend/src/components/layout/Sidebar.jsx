// src/components/Layout/SideBar.jsx
import React from 'react';

const SideBar = ({ user }) => {
  return (
    <div className="bg-gray-800 text-white w-64 min-h-screen p-4">
      <div className="space-y-6">
        <div className="p-2">
          <h2 className="text-xl font-bold">Menu</h2>
        </div>
        <nav>
          <ul className="space-y-2">
            <li>
              <a href="/" className="block p-2 hover:bg-gray-700 rounded">
                Dashboard
              </a>
            </li>
            {user?.role === 'admin' && (
              <li>
                <a href="/admin/users" className="block p-2 hover:bg-gray-700 rounded">
                  Gestion Utilisateurs
                </a>
              </li>
            )}
          </ul>
        </nav>
      </div>
    </div>
  );
};

export default SideBar;