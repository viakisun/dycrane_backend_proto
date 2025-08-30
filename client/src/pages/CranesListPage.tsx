import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import apiClient from '../apiClient';

// Assuming CraneStatus and CraneOut schemas are defined somewhere accessible
// For now, defining them locally for clarity
enum CraneStatus {
    NORMAL = "NORMAL",
    REPAIR = "REPAIR",
    INBOUND = "INBOUND",
}

interface Crane {
    id: string;
    model_name: string;
    serial_no: string;
    status: CraneStatus;
}

const CranesListPage: React.FC = () => {
    const { ownerId } = useParams<{ ownerId: string }>();
    const [cranes, setCranes] = useState<Crane[]>([]);
    const [statusFilter, setStatusFilter] = useState<CraneStatus | ''>('');
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchCranes = async () => {
            if (!ownerId) return;
            try {
                setLoading(true);
                const endpoint = statusFilter
                    ? `/owners/${ownerId}/cranes?status=${statusFilter}`
                    : `/owners/${ownerId}/cranes`;
                const response = await apiClient.get(endpoint);
                setCranes(response.data);
                setError(null);
            } catch (err) {
                setError('Failed to fetch crane data.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchCranes();
    }, [ownerId, statusFilter]);

    // Handler for deployment request (placeholder)
    const handleDeployRequest = (craneId: string) => {
        alert(`Requesting deployment for crane: ${craneId}`);
        // In a real implementation, this would open a modal or navigate to a new page
        // to collect details (e.g., site_id, notes) and then call the
        // POST /api/cranes/{craneId}/deploy-requests endpoint.
    };

    if (loading) return <div className="text-center text-cyan-glow">Loading Cranes...</div>;
    if (error) return <div className="text-center text-red-500">{error}</div>;

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-cyan-glow">Cranes for Owner {ownerId}</h1>
                <div>
                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value as CraneStatus | '')}
                        className="bg-gray-800 border border-gray-600 text-white rounded-md p-2"
                    >
                        <option value="">All Statuses</option>
                        <option value={CraneStatus.NORMAL}>Normal</option>
                        <option value={CraneStatus.REPAIR}>Repair</option>
                        <option value={CraneStatus.INBOUND}>Inbound</option>
                    </select>
                </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {cranes.map((crane) => (
                    <div key={crane.id} className="bg-gray-800 p-6 rounded-lg border border-gray-700 flex flex-col justify-between">
                        <div>
                            <h2 className="text-xl font-bold text-white">{crane.model_name}</h2>
                            <p className="text-sm text-gray-400">{crane.serial_no}</p>
                        </div>
                        <div className="mt-4 flex justify-between items-center">
                            <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                                crane.status === CraneStatus.NORMAL ? 'bg-green-500/20 text-green-300' :
                                crane.status === CraneStatus.REPAIR ? 'bg-yellow-500/20 text-yellow-300' :
                                'bg-blue-500/20 text-blue-300'
                            }`}>{crane.status}</span>
                            <button
                                onClick={() => handleDeployRequest(crane.id)}
                                disabled={crane.status !== CraneStatus.NORMAL}
                                className="px-4 py-2 text-sm font-bold text-white bg-cyan-600 rounded-md hover:bg-cyan-500 disabled:bg-gray-600 disabled:cursor-not-allowed"
                            >
                                Deploy
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CranesListPage;
