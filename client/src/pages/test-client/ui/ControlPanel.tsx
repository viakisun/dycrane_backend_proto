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
        <div className="text-center p-4">
            <button
                onClick={handleRun}
                disabled={isRunning}
                className={cn(
                    "px-6 py-3 text-base font-bold uppercase tracking-wider text-white transition-colors duration-200 rounded-md",
                    "bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 disabled:cursor-not-allowed"
                )}
            >
                {isRunning ? 'Executing...' : 'Run Full Workflow'}
            </button>
        </div>
    );
};
