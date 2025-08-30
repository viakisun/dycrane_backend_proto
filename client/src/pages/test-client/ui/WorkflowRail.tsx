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
      return <span className="text-gray-500">●</span>;
  }
};

const WorkflowRail: React.FC = () => {
  const { stepStatus, selectedStep, actions } = useWorkflowStore();
  const { runStep, runAllSteps, setSelectedStep } = actions;

  return (
    <div className="bg-gray-800 text-white p-4 rounded-lg">
      <h2 className="text-lg font-bold mb-4">Workflow Steps</h2>
      <ul>
        {WORKFLOW_STEPS.map((step) => (
          <li
            key={step.code}
            className={`flex items-center justify-between mb-2 p-2 rounded cursor-pointer ${selectedStep === step.code ? 'bg-gray-700' : ''}`}
            onClick={() => setSelectedStep(step.code)}
          >
            <div className="flex items-center">
              <span className="mr-2">{getStatusIcon(stepStatus[step.code])}</span>
              <span>{step.code}: {step.title}</span>
            </div>
            <button
              className="bg-blue-600 hover:bg-blue-700 text-white text-xs py-1 px-2 rounded"
              onClick={(e) => {
                e.stopPropagation();
                runStep(step.code);
              }}
            >
              Run
            </button>
          </li>
        ))}
      </ul>
      <button
        className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded mt-4"
        onClick={runAllSteps}
      >
        Auto Run All
      </button>
    </div>
  );
};

export default WorkflowRail;
