import React, { useState, useEffect } from 'react';
import apiClient from '../apiClient';
import { Link } from 'react-router-dom';

interface OwnerStats {
  id: string;
  name: string;
  total_cranes: number;
  available_cranes: number;
}

const OwnersListPage: React.FC = () => {
  const [owners, setOwners] = useState<OwnerStats[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOwners = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get('/owners/with-stats');
        setOwners(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch owner data. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchOwners();
  }, []);

  if (loading) {
    return <div className="text-center text-cyan-glow">Loading Owners...</div>;
  }

  if (error) {
    return <div className="text-center text-red-500">{error}</div>;
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-cyan-glow mb-6">Owner Organizations</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {owners.map((owner) => (
          <Link
            to={`/owners/${owner.id}/cranes`}
            key={owner.id}
            state={{ ownerName: owner.name }}
            className="block p-1 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 hover:scale-105 transition-transform duration-300"
          >
            <div className="bg-gray-800 p-6 rounded-md h-full">
              <h2 className="text-xl font-bold text-white">{owner.name}</h2>
              <div className="mt-4 flex justify-between items-center">
                <span className="text-gray-400">Total Cranes:</span>
                <span className="text-2xl font-bold text-cyan-400">{owner.total_cranes}</span>
              </div>
              <div className="mt-2 flex justify-between items-center">
                <span className="text-gray-400">Available:</span>
                <span className="text-2xl font-bold text-green-400">{owner.available_cranes}</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default OwnersListPage;
