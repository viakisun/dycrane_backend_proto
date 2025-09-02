import React, { useState, useEffect } from 'react';
import { useWorkflowStore } from '../state/workflowStore';
import { StepDefinition } from '../workflow-def';
import { StepHeader } from './StepHeader';
import { StepDetails } from './StepDetails';
import { StepLogOutput } from './StepLogOutput';
import { StepStatus } from '../state/workflowStore';

interface WorkflowStepCardProps {
  step: StepDefinition;
}

const getStatusColor = (status: StepStatus) => {
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

const StatusSpinner: React.FC = () => (
  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
);

const StatusCheck: React.FC = () => (
    <svg className="h-5 w-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
);

const StatusCross: React.FC = () => (
    <svg className="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
);


const StatusIndicator: React.FC<{ status: StepStatus }> = ({ status }) => {
    if (status === 'idle') return null;

    const statusMap = {
      'in-progress': { icon: <StatusSpinner />, text: 'Running...', color: 'text-blue-500' },
      'done': { icon: <StatusCheck />, text: 'Success', color: 'text-green-500' },
      'error': { icon: <StatusCross />, text: 'Failed', color: 'text-red-500' },
    };

    const currentStatus = statusMap[status];

    if (!currentStatus) return null;

    return (
      <div className={`flex items-center text-sm font-semibold ${currentStatus.color}`}>
        {currentStatus.icon}
        <span>{currentStatus.text}</span>
      </div>
    );
};


export const WorkflowStepCard: React.FC<WorkflowStepCardProps> = ({ step }) => {
  const { stepStatus, logsByStepCode, isRunning, actions } = useWorkflowStore();
  const { runStep } = actions;
  const status = stepStatus[step.code];
  const logs = logsByStepCode[step.code] || [];
  const [showLogs, setShowLogs] = useState(false);

  useEffect(() => {
    if (status === 'idle') {
      setShowLogs(false);
    }
  }, [status]);

  const handleRun = () => {
    setShowLogs(true);
    runStep(step.code);
  };

  return (
    <div className={`bg-white p-6 rounded-lg shadow-sm border-l-4 ${getStatusColor(status)} mb-4 transition-colors duration-300`}>
      <div className="flex justify-between items-center">
        <StepHeader step={step} />
        <div className="flex items-center space-x-4">
            <StatusIndicator status={status} />
            <button
                onClick={handleRun}
                disabled={isRunning || status === 'in-progress'}
                className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
            >
                Run
            </button>
        </div>
      </div>
      <StepDetails step={step} />
      {showLogs && <StepLogOutput logs={logs} />}
    </div>
  );
};
