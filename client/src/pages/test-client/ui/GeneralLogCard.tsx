import React from 'react';
import { useWorkflowStore } from '../state/workflowStore';
import { StepLogOutput } from './StepLogOutput';

export const GeneralLogCard: React.FC = () => {
  const { generalLogs } = useWorkflowStore();

  return (
    <div className="bg-gray-50 p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
      <h2 className="text-lg font-semibold text-gray-700 mb-2">Execution Log</h2>
      <div className="max-h-48 overflow-y-auto">
        <StepLogOutput logs={generalLogs} />
      </div>
    </div>
  );
};
