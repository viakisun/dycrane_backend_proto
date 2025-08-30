import React, { useRef, useEffect } from 'react';
import { useWorkflowStore } from '../state/workflowStore';

const LogConsole: React.FC = () => {
  const { logs } = useWorkflowStore();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="bg-white p-4 rounded-lg h-full flex flex-col font-mono shadow-sm border border-gray-200">
      <h2 className="text-lg font-bold mb-4 text-gray-700">Log Console</h2>
      <div ref={scrollRef} className="flex-grow overflow-y-auto pr-2 text-xs bg-gray-50 p-2 rounded">
        <div className="grid grid-cols-[auto_auto_auto_1fr] gap-x-3 gap-y-1">
            {logs.map((log, index) => (
            <React.Fragment key={index}>
                <div className="text-gray-400">{log.time}</div>
                <div className="text-blue-600 font-semibold">{log.actor}</div>
                <div className="text-green-600">{log.stepCode}</div>
                <div className="text-gray-800">{log.summary}</div>
            </React.Fragment>
            ))}
        </div>
      </div>
    </div>
  );
};

export default LogConsole;
