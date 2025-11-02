import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Home: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-100">
      <div className="container mx-auto px-4 py-8">
        <nav className="bg-white rounded-lg shadow-md p-4 mb-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Pasky</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Logout
          </button>
        </nav>

        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-indigo-100 rounded-full mb-4">
                <svg
                  className="w-10 h-10 text-indigo-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                Welcome, {user?.username}!
              </h2>
              <p className="text-gray-600">
                You have successfully authenticated using a passkey.
              </p>
            </div>

            <div className="border-t pt-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Account Information
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600 font-medium">Username:</span>
                  <span className="text-gray-900">{user?.username}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600 font-medium">Email:</span>
                  <span className="text-gray-900">{user?.email}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-gray-600 font-medium">User ID:</span>
                  <span className="text-gray-900">{user?.id}</span>
                </div>
              </div>
            </div>

            <div className="mt-8 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800 text-sm">
                <strong>✓ Authenticated</strong> - Your session is secure and protected by passkey authentication.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;

