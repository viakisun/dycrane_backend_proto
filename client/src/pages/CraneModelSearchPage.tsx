import React, { useState, useEffect } from 'react';
import apiClient from '../apiClient';

interface CraneModel {
    id: string;
    model_name: string;
    max_lifting_capacity_ton_m?: number;
    max_working_height_m?: number;
    max_working_radius_m?: number;
}

const CraneModelSearchPage: React.FC = () => {
    const [models, setModels] = useState<CraneModel[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    // Add state for search filters here

    useEffect(() => {
        const fetchModels = async () => {
            try {
                setLoading(true);
                // Add filter query params to the endpoint as needed
                const response = await apiClient.get('/catalog/crane-models');
                setModels(response.data);
                setError(null);
            } catch (err) {
                setError('Failed to fetch crane models.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchModels();
    }, []); // Add filters to dependency array when implemented

    if (loading) return <div className="text-center text-cyan-glow">Loading Models...</div>;
    if (error) return <div className="text-center text-red-500">{error}</div>;

    return (
        <div>
            <h1 className="text-3xl font-bold text-cyan-glow mb-6">Search Crane Models</h1>
            {/* Add filter inputs here */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {models.map((model) => (
                    <div key={model.id} className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                        <h2 className="text-xl font-bold text-white">{model.model_name}</h2>
                        <div className="mt-2 text-sm text-gray-400 space-y-1">
                            <p>Max Lift: {model.max_lifting_capacity_ton_m || 'N/A'} ton·m</p>
                            <p>Max Height: {model.max_working_height_m || 'N/A'} m</p>
                            <p>Max Radius: {model.max_working_radius_m || 'N/A'} m</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CraneModelSearchPage;
