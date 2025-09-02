import React from 'react';
import { StepDefinition } from '../workflow-def';

interface StepHeaderProps {
  step: StepDefinition;
  isRunning: boolean;
  onRun: () => void;
}

export const StepHeader: React.FC<StepHeaderProps> = ({ step, isRunning, onRun }) => {
  return (
    <div className="flex justify-between items-start">
      <div>
        <h2 className="text-xl font-bold text-gray-800">{step.code}: {step.title}</h2>
        <p className="text-sm text-gray-500 mt-1">
          <span className="font-semibold">Actor:</span> {step.actor}
        </p>
      </div>
      <button
        onClick={onRun}
        disabled={isRunning}
        className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Run
      </button>
    </div>
  );
};
