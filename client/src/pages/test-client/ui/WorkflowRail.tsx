import React from 'react';
import { useWorkflowStore } from '../state/workflowStore';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: any[]) {
  return twMerge(clsx(inputs));
}

type Step = {
  code: string;
  name: string;
};

type WorkflowRailProps = {
  steps: Step[];
};

export const WorkflowRail: React.FC<WorkflowRailProps> = ({ steps }) => {
  const { stepStatus, currentStep } = useWorkflowStore();

  return (
    <div className="bg-gray-900 bg-opacity-70 p-6 rounded-lg border border-gray-700 h-full">
      <h2 className="text-lg font-bold text-gray-300 mb-4 text-center uppercase tracking-wider">Workflow Steps</h2>
      <div className="relative">
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-700" />
        {steps.map((step, index) => {
          const status = stepStatus[step.code] || 'pending';
          const isCurrent = currentStep === step.code;
          const isCompleted = status === 'success';
          const isFailed = status === 'error';
          const isRunning = status === 'running';

          return (
            <div key={step.code} className="flex items-center mb-4 last:mb-0">
              <div className="relative z-10">
                <div
                  className={cn(
                    'w-8 h-8 rounded-full flex items-center justify-center border-2',
                    {
                      'border-blue-500 bg-blue-900': isCurrent || isRunning,
                      'border-green-500 bg-green-900': isCompleted,
                      'border-red-500 bg-red-900': isFailed,
                      'border-gray-600 bg-gray-800': status === 'pending',
                    }
                  )}
                >
                  <span className="text-sm font-bold">{index + 1}</span>
                </div>
              </div>
              <span
                className={cn('ml-4 text-sm font-medium', {
                  'text-white': isCurrent || isRunning,
                  'text-green-400': isCompleted,
                  'text-red-400': isFailed,
                  'text-gray-400': status === 'pending',
                })}
              >
                {step.name}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
