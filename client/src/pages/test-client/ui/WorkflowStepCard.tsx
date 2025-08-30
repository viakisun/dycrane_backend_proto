import React, { useState } from 'react';
import { useWorkflowStore, Log } from '../state/workflowStore';
import { StepDefinition } from '../workflow-def';

interface WorkflowStepCardProps {
  step: StepDefinition;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'in-progress':
      return 'border-blue-500';
    case 'done':
      return 'border-green-500';
    case 'error':
      return 'border-red-500';
    case 'idle':
    default:
      return 'border-gray-300';
  }
};

export const WorkflowStepCard: React.FC<WorkflowStepCardProps> = ({ step }) => {
  const { stepStatus, logsByStepCode, isRunning, actions } = useWorkflowStore();
  const { runStep } = actions;
  const status = stepStatus[step.code];
  const logs = logsByStepCode[step.code] || [];
  const [showLogs, setShowLogs] = useState(false);

  const handleRun = () => {
    setShowLogs(true);
    runStep(step.code);
  };

  return (
    <div className={`bg-white p-6 rounded-lg shadow-md border-l-4 ${getStatusColor(status)} mb-4`}>
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-xl font-bold text-gray-800">{step.code}: {step.title}</h2>
          <p className="text-sm text-gray-500 mt-1">
            <span className="font-semibold">Actor:</span> {step.actor}
          </p>
        </div>
        <button
          onClick={handleRun}
          disabled={isRunning}
          className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Run
        </button>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-gray-700 mb-4">{step.description}</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h4 className="font-semibold text-gray-600">Data In (from context)</h4>
            <pre className="bg-gray-50 p-2 mt-1 rounded text-xs font-mono text-green-700">
              <code>{step.dataFlow.in.join('\n') || 'N/A'}</code>
            </pre>
          </div>
          <div>
            <h4 className="font-semibold text-gray-600">Data Out (to context)</h4>
            <pre className="bg-gray-50 p-2 mt-1 rounded text-xs font-mono text-orange-700">
              <code>{step.dataFlow.out.join('\n') || 'N/A'}</code>
            </pre>
          </div>
          <div>
            <h4 className="font-semibold text-gray-600">API Endpoint</h4>
            <pre className="bg-gray-50 p-2 mt-1 rounded text-xs font-mono text-purple-700">
              <code>{step.api?.method} {step.api?.path}</code>
            </pre>
          </div>
          <div>
            <h4 className="font-semibold text-gray-600">Sample Request Body</h4>
            <pre className="bg-gray-50 p-2 mt-1 rounded text-xs font-mono text-gray-600 max-h-28 overflow-y-auto">
              <code>{step.api?.sample}</code>
            </pre>
          </div>
        </div>
      </div>

      {showLogs && (
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
      )}
    </div>
  );
};
