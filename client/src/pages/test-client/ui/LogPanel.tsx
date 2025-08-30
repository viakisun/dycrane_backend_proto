import React from 'react';
import { useWorkflowStore, LogEntry } from '../state/workflowStore';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
function cn(...inputs: any[]) {
    return twMerge(clsx(inputs));
}

const renderLogData = (data: any) => {
    if (!data || Object.keys(data).length === 0) return null;
    const formatted = JSON.stringify(data, null, 2);
    return <pre className="bg-black bg-opacity-50 p-2 rounded-lg text-xs mt-1">{formatted}</pre>;
};

export const LogPanel: React.FC = () => {
    const logs = useWorkflowStore((state) => state.logs);
    const logContainerRef = React.useRef<HTMLDivElement>(null);

    React.useEffect(() => {
        if (logContainerRef.current) {
            logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className="bg-gray-900 bg-opacity-70 p-6 rounded-lg border border-gray-700 flex-grow">
            <h2 className="text-lg font-bold text-gray-300 mb-4 text-center uppercase tracking-wider">Real-Time Logs</h2>
            <div ref={logContainerRef} className="h-96 overflow-y-auto p-4 bg-black bg-opacity-75 rounded-lg border border-gray-600 font-mono text-sm">
                {logs.map((log, index) => (
                    <div key={index} className={cn("flex items-start mb-1", {
                        'text-red-400': log.type === 'error',
                        'text-green-400': log.type === 'success',
                        'text-blue-400': log.type === 'info',
                        'text-yellow-300': log.type === 'request',
                        'text-purple-400': log.type === 'response',
                     })}>
                        <span className="mr-2 text-gray-500">{`[${log.time.split('T')[1].slice(0, 8)}]`}</span>
                        <span className="mr-2 font-bold uppercase w-32 text-gray-400">{`[${log.actor}]`}</span>
                        <div className="flex-1">
                            <span>{log.summary}</span>
                            {log.extracted && renderLogData(log.extracted)}
                            {log.forwarded && renderLogData(log.forwarded)}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
