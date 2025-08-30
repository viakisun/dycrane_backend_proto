import React, { useState, useEffect } from 'react';
import apiClient from '../apiClient';

// Placeholder data and types
interface Request {
    id: string;
    type: string;
    status: string;
    requester_id: string;
    target_entity_id: string; // crane_id
    related_entity_id: string; // site_id
}

const placeholderRequests: Request[] = [
    { id: 'req-001', type: 'CRANE_DEPLOY', status: 'PENDING', requester_id: 'user-safety-manager-01', target_entity_id: 'crane-001', related_entity_id: 'site-001' },
    { id: 'req-002', type: 'CRANE_DEPLOY', status: 'PENDING', requester_id: 'user-safety-manager-02', target_entity_id: 'crane-002', related_entity_id: 'site-002' },
];

const RequestsListPage: React.FC = () => {
    const [requests, setRequests] = useState<Request[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchRequests = async () => {
            try {
                setLoading(true);
                const response = await apiClient.get('/owners/me/requests?type=CRANE_DEPLOY&status=PENDING&user_id=user-owner-01'); // Added user_id for now
                setRequests(response.data);
                setError(null);
            } catch (err) {
                setError('Failed to fetch requests.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchRequests();
    }, []);

    const handleResponse = async (requestId: string, approve: boolean) => {
        try {
            const payload = {
                status: approve ? 'APPROVED' : 'REJECTED',
                approver_id: 'user-owner-01', // This should be the current user's ID
                notes: approve ? 'Deployment approved.' : 'Deployment rejected.'
            };
            await apiClient.post(`/requests/${requestId}/respond`, payload);

            // Refresh list by filtering out the responded request
            setRequests(prev => prev.filter(req => req.id !== requestId));
            alert(`Request ${requestId} has been ${approve ? 'approved' : 'rejected'}.`);

        } catch (err) {
            alert('Failed to respond to request.');
            console.error(err);
        }
    };

    if (loading) return <div className="text-center text-cyan-glow">Loading Requests...</div>;
    if (error) return <div className="text-center text-red-500">{error}</div>;

    return (
        <div>
            <h1 className="text-3xl font-bold text-cyan-glow mb-6">Pending Deployment Requests</h1>
            <div className="space-y-4">
                {requests.length > 0 ? requests.map((req) => (
                    <div key={req.id} className="bg-gray-800 p-4 rounded-lg border border-gray-700 flex items-center justify-between">
                        <div>
                            <p className="font-bold text-white">Request ID: {req.id}</p>
                            <p className="text-sm text-gray-400">Crane: {req.target_entity_id} for Site: {req.related_entity_id}</p>
                        </div>
                        <div className="flex items-center space-x-4">
                            <button onClick={() => handleResponse(req.id, true)} className="px-4 py-2 text-sm font-bold text-white bg-green-600 rounded-md hover:bg-green-500">
                                Approve
                            </button>
                            <button onClick={() => handleResponse(req.id, false)} className="px-4 py-2 text-sm font-bold text-white bg-red-600 rounded-md hover:bg-red-500">
                                Reject
                            </button>
                        </div>
                    </div>
                )) : (
                    <p className="text-gray-400">No pending requests found.</p>
                )}
            </div>
        </div>
    );
};

export default RequestsListPage;
