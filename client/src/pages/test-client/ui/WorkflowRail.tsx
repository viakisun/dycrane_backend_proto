import React from 'react';
import { useWorkflowStore } from '../state/workflowStore';
import { WORKFLOW_STEPS } from '../workflow-def';
import { StepStatus } from '../state/workflowStore';

const getStatusIcon = (status: StepStatus) => {
  switch (status) {
    case 'in-progress':
      return <span className="text-blue-400">►</span>;
    case 'done':
      return <span className="text-green-400">✓</span>;
    case 'error':
      return <span className="text-red-400">✗</span>;
    case 'idle':
    default:
      return <span className="text-gray-500">●</span>;
  }
};

const WorkflowRail: React.FC = () => {
  const { stepStatus, selectedStep, isRunning, actions } = useWorkflowStore();
  const { runStep, runAllSteps, setSelectedStep } = actions;

  return (
    <div className="bg-[#252526] p-4 rounded-lg h-full">
      <h2 className="text-lg font-bold mb-4 text-gray-300">Workflow Steps</h2>
      <ul className="space-y-1">
        {WORKFLOW_STEPS.map((step) => (
          <li
            key={step.code}
            className={`flex items-center justify-between p-2 rounded cursor-pointer transition-colors duration-150 ${selectedStep === step.code ? 'bg-[#37373d]' : 'hover:bg-[#2a2d2e]'}`}
            onClick={() => setSelectedStep(step.code)}
          >
            <div className="flex items-center">
              <span className="mr-3 w-4">{getStatusIcon(stepStatus[step.code])}</span>
              <span className="text-sm">{step.code}: {step.title}</span>
            </div>
            <button
              className="bg-[#0e639c] hover:bg-[#1177bb] text-white text-xs py-1 px-2 rounded transition-colors duration-150 disabled:opacity-50"
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
        className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded mt-6 transition-colors duration-150 disabled:opacity-50"
        onClick={runAllSteps}
        disabled={isRunning}
      >
        {isRunning ? 'Running...' : 'Auto Run All'}
      </button>
    </div>
  );
};

export default WorkflowRail;
