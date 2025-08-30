import React from 'react';
import { useWorkflowStore } from '../state/workflowStore';

const LogConsole: React.FC = () => {
  const { logs } = useWorkflowStore();

  return (
    <div className="bg-gray-900 text-white font-mono p-4 rounded-lg h-96 overflow-y-auto">
      <div className="grid grid-cols-[auto_auto_auto_1fr] gap-x-4 text-sm">
        <div className="font-bold">TIME</div>
        <div className="font-bold">ACTOR</div>
        <div className="font-bold">STEP</div>
        <div className="font-bold">SUMMARY</div>
        {logs.map((log, index) => (
          <React.Fragment key={index}>
            <div className="text-gray-500">{log.time}</div>
            <div className="text-blue-400">{log.actor}</div>
            <div className="text-green-400">{log.stepCode}</div>
            <div>{log.summary}</div>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

export default LogConsole;
