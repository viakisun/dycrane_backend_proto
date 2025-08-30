import React from 'react';
import { useWorkflowStore } from '../state/workflowStore';
import { WORKFLOW_STEPS } from '../workflow-def';
import { WorkflowStepCard } from './test-client/ui/WorkflowStepCard';

const TestClientPage: React.FC = () => {
  const { isRunning, actions } = useWorkflowStore();
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
                disabled={isRunning}
                className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded transition-colors duration-150 disabled:opacity-50"
            >
                Reset Data
            </button>
            <button
                onClick={runAllSteps}
                disabled={isRunning}
                className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition-colors duration-150 disabled:opacity-50"
            >
                {isRunning ? 'Running...' : 'Run All Steps'}
            </button>
        </div>
      </header>

      <div className="space-y-6">
        {WORKFLOW_STEPS.map((step) => (
          <WorkflowStepCard key={step.code} step={step} />
        ))}
      </div>
    </div>
  );
};

export default TestClientPage;
