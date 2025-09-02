import React, { useState } from 'react';
import { useWorkflowStore } from '../state/workflowStore';
import { StepDefinition } from '../workflow-def';
import { StepHeader } from './StepHeader';
import { StepDetails } from './StepDetails';
import { StepLogOutput } from './StepLogOutput';

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
    <div className={`bg-white p-6 rounded-lg shadow-sm border-l-4 ${getStatusColor(status)} mb-4`}>
      <StepHeader step={step} isRunning={isRunning} onRun={handleRun} />
      <StepDetails step={step} />
      {showLogs && <StepLogOutput logs={logs} />}
    </div>
  );
};
