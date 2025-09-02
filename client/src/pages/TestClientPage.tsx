import React from 'react';
import { useWorkflowStore, Log } from './test-client/state/workflowStore';
import { WORKFLOW_STEPS } from './test-client/workflow-def';
import { WorkflowStepCard } from './test-client/ui/WorkflowStepCard';

const GlobalLog: React.FC<{ log: Log }> = ({ log }) => {
    const baseClasses = "text-sm p-3 rounded-md mb-4";
    const successClasses = "bg-green-100 text-green-800";
    const errorClasses = "bg-red-100 text-red-800";

    return (
        <div className={`${baseClasses} ${log.isError ? errorClasses : successClasses}`}>
            <span className="font-semibold">{log.actor}:</span> {log.summary}
        </div>
    );
};


const TestClientPage: React.FC = () => {
  const { isRunning, isResetting, globalLog, actions } = useWorkflowStore();
  const { runAllSteps, fullReset } = actions;

  return (
    <div className="p-4 md:p-6 lg:p-8 max-w-4xl mx-auto">
      <header className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Developer Guide: Workflow</h1>
          <p className="text-sm text-gray-500">
            An interactive step-by-step guide to the business workflow.
          </p>
        </div>
        <div className="flex items-center space-x-2">
            <button
                onClick={fullReset}
                disabled={isRunning || isResetting}
                className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded transition-colors duration-150 disabled:opacity-50"
            >
                {isResetting ? 'Resetting...' : 'Reset Data'}
            </button>
            <button
                onClick={runAllSteps}
                disabled={isRunning || isResetting}
                className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition-colors duration-150 disabled:opacity-50"
            >
                {isRunning ? 'Running...' : 'Run All Steps'}
            </button>
        </div>
      </header>

      {globalLog && <GlobalLog log={globalLog} />}

      <div className="space-y-6">
        {WORKFLOW_STEPS.map((step) => (
          <WorkflowStepCard key={step.code} step={step} />
        ))}
      </div>
    </div>
  );
};

export default TestClientPage;
