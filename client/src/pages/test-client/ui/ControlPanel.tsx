import React from 'react';
import { useWorkflowStore } from '../state/workflowStore';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: any[]) {
    return twMerge(clsx(inputs));
}

type ControlPanelProps = {
    onRunWorkflow: () => void;
};

// TODO: Move this to a config file or UI inputs
const hardcodedConfig = {
    host: 'http://localhost:8000',
    port: 8000,
    users: {
        SAFETY_MANAGER: { id: "user-safety-manager-01", token: "token-safety-manager-01" },
        MANUFACTURER: { id: "user-manufacturer-01", token: "token-manufacturer-01" },
        OWNER: { id: "user-owner-01", orgId: "org-owner-01", token: "token-owner-01" },
        DRIVER: { id: "user-driver-01", token: "token-driver-01" },
    }
};


export const ControlPanel: React.FC<ControlPanelProps> = ({ onRunWorkflow }) => {
    const { isRunning, actions } = useWorkflowStore();

    const handleRun = () => {
        actions.startWorkflow(hardcodedConfig);
        onRunWorkflow();
    };

    return (
        <div className="text-center">
            <button
                onClick={handleRun}
                disabled={isRunning}
                className={cn(
                    "px-8 py-4 text-lg font-bold uppercase tracking-widest text-white transition-all duration-300 rounded-lg",
                    "bg-cyan-600 hover:bg-cyan-500 disabled:bg-gray-700 disabled:cursor-not-allowed",
                    "shadow-lg shadow-cyan-500/20 hover:shadow-xl hover:shadow-cyan-500/40",
                    "transform hover:-translate-y-1",
                    { "animate-pulse": !isRunning }
                )}
            >
                {isRunning ? 'Executing Workflow...' : 'Initiate Full Workflow'}
            </button>
        </div>
    );
};
