import React, { useState, useEffect } from 'react';
import { useWorkflowStore, StepStatus } from '../state/workflowStore';
import { StepDefinition } from '../workflow-def';
import { StepHeader } from './StepHeader';
import { StepDetails } from './StepDetails';
import { StepLogOutput } from './StepLogOutput';

interface WorkflowStepCardProps {
  step: StepDefinition;
}

const getStatusBorderColor = (status: StepStatus) => {
  switch (status) {
    case 'in-progress': return 'border-blue-500';
    case 'done': return 'border-green-500';
    case 'error': return 'border-red-500';
    default: return 'border-gray-300';
  }
};

const getStatusBgColor = (status: StepStatus) => {
    switch (status) {
      case 'in-progress': return 'bg-blue-50';
      case 'done': return 'bg-green-50';
      case 'error': return 'bg-red-50';
      default: return 'bg-white';
    }
  };

export const WorkflowStepCard: React.FC<WorkflowStepCardProps> = ({ step }) => {
  const { stepStatus, logsByStepCode, isRunning, actions } = useWorkflowStore();
  const { runStep } = actions;
  const status = stepStatus[step.code];
  const logs = logsByStepCode[step.code] || [];
  const [showLogs, setShowLogs] = useState(false);

  useEffect(() => {
    if (status === 'in-progress' || status === 'done' || status === 'error') {
      setShowLogs(true);
    } else if (status === 'idle') {
        setShowLogs(false);
    }
  }, [status]);

  const handleRun = () => {
    runStep(step.code);
  };

  return (
    <div className={`p-6 rounded-lg shadow-sm border-l-4 ${getStatusBorderColor(status)} ${getStatusBgColor(status)} mb-4`}>
      <StepHeader step={step} isRunning={isRunning} onRun={handleRun} />
      <StepDetails step={step} />
      {showLogs && <StepLogOutput logs={logs} />}
    </div>
  );
};
