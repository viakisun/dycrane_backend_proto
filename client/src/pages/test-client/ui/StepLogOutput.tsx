import React from 'react';
import { Log } from '../state/workflowStore';

interface StepLogOutputProps {
  logs: Log[];
}

export const StepLogOutput: React.FC<StepLogOutputProps> = ({ logs }) => {
  if (logs.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 pt-4 border-t border-gray-200">
      <h4 className="font-semibold text-gray-600 mb-2">Execution Log</h4>
      <div className="bg-gray-800 text-white font-mono text-xs p-3 rounded max-h-48 overflow-y-auto">
        {logs.map((log, index) => (
          <p key={index} className={`whitespace-pre-wrap ${log.isError ? 'text-red-400' : ''}`}>
            <span className="text-gray-500 mr-2">{log.time}</span>
            <span className="text-blue-400 font-bold mr-2">[{log.actor}]</span>
            {log.summary}
          </p>
        ))}
      </div>
    </div>
  );
};
