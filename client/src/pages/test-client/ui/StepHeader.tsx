import React from 'react';
import { StepDefinition } from '../workflow-def';

interface StepHeaderProps {
  step: StepDefinition;
}

export const StepHeader: React.FC<StepHeaderProps> = ({ step }) => {
  return (
    <div>
      <h2 className="text-xl font-bold text-gray-800">{step.code}: {step.title}</h2>
      <p className="text-sm text-gray-500 mt-1">
        <span className="font-semibold">Actor:</span> {step.actor}
      </p>
    </div>
  );
};
