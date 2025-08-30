import React from 'react';
import { useWorkflowStore } from '../state/workflowStore';
import { WORKFLOW_STEPS } from '../workflow-def';
import { StepStatus } from '../state/workflowStore';

const getStatusIcon = (status: StepStatus) => {
  switch (status) {
    case 'in-progress':
      return <span className="text-blue-500">►</span>;
    case 'done':
      return <span className="text-green-500">✓</span>;
    case 'error':
      return <span className="text-red-500">✗</span>;
    case 'idle':
    default:
      return <span className="text-gray-400">●</span>;
  }
};

const WorkflowRail: React.FC = () => {
  const { stepStatus, selectedStep, isRunning, actions } = useWorkflowStore();
  const { runStep, runAllSteps, setSelectedStep } = actions;

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm h-full border border-gray-200">
      <h2 className="text-lg font-bold mb-4 text-gray-700">Workflow Steps</h2>
      <ul className="space-y-1">
        {WORKFLOW_STEPS.map((step) => (
          <li
            key={step.code}
            className={`flex items-center justify-between p-2 rounded cursor-pointer transition-colors duration-150 ${selectedStep === step.code ? 'bg-blue-50 text-blue-800' : 'hover:bg-gray-50'}`}
            onClick={() => setSelectedStep(step.code)}
          >
            <div className="flex items-center">
              <span className="mr-3 w-4">{getStatusIcon(stepStatus[step.code])}</span>
              <span className="text-sm font-medium">{step.code}: {step.title}</span>
            </div>
            <button
              className="bg-blue-500 hover:bg-blue-600 text-white text-xs font-bold py-1 px-2 rounded transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={(e) => {
                e.stopPropagation();
                runStep(step.code);
              }}
              disabled={isRunning}
            >
              Run
            </button>
          </li>
        ))}
      </ul>
      <button
        className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded mt-6 transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
        onClick={runAllSteps}
        disabled={isRunning}
      >
        {isRunning ? 'Running...' : 'Auto Run All'}
      </button>
    </div>
  );
};

export default WorkflowRail;
