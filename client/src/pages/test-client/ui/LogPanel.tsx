import React from 'react';
import { useWorkflowStore, LogEntry } from '../state/workflowStore';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import GlitchText from '../../../components/GlitchText';

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
        <div className="bg-black bg-opacity-30 p-6 rounded-lg border border-cyan-glow/20 flex-grow">
            <h2 className="text-xl font-bold text-cyan-glow mb-6 text-center uppercase tracking-widest">Real-Time Logs</h2>
            <div ref={logContainerRef} className="h-96 overflow-y-auto p-4 bg-black bg-opacity-50 rounded-lg border border-gray-700">
                {logs.map((log, index) => (
                    <div key={index} className={cn("flex items-start mb-2 text-sm", {
                        'text-red-400': log.type === 'error',
                        'text-green-400': log.type === 'success',
                        'text-cyan-300': log.type === 'info',
                        'text-yellow-400': log.type === 'request',
                        'text-purple-400': log.type === 'response',
                     })}>
                        <span className="mr-2 font-mono">{`[${log.time.split('T')[1].slice(0, 8)}]`}</span>
                        <span className="mr-2 font-bold uppercase w-32">{`[${log.actor}]`}</span>
                        <div className="flex-1">
                            <GlitchText text={log.summary} />
                            {log.extracted && renderLogData(log.extracted)}
                            {log.forwarded && renderLogData(log.forwarded)}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
