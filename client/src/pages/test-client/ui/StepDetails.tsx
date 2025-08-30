import React from 'react';
import { StepDefinition } from '../workflow-def';

interface StepDetailsProps {
  step: StepDefinition;
}

export const StepDetails: React.FC<StepDetailsProps> = ({ step }) => {
  return (
    <div className="mt-4 pt-4 border-t border-gray-200">
      <p className="text-gray-700 mb-4">{step.description}</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div>
          <h4 className="font-semibold text-gray-600">Data In (from context)</h4>
          <pre className="bg-gray-50 p-2 mt-1 rounded text-xs font-mono text-green-700">
            <code>{step.dataFlow.in.join('\n') || 'N/A'}</code>
          </pre>
        </div>
        <div>
          <h4 className="font-semibold text-gray-600">Data Out (to context)</h4>
          <pre className="bg-gray-50 p-2 mt-1 rounded text-xs font-mono text-orange-700">
            <code>{step.dataFlow.out.join('\n') || 'N/A'}</code>
          </pre>
        </div>
        <div>
          <h4 className="font-semibold text-gray-600">API Endpoint</h4>
          <pre className="bg-gray-50 p-2 mt-1 rounded text-xs font-mono text-purple-700">
            <code>{step.api?.method} {step.api?.path}</code>
          </pre>
        </div>
        <div>
          <h4 className="font-semibold text-gray-600">Sample Request Body</h4>
          <pre className="bg-gray-50 p-2 mt-1 rounded text-xs font-mono text-gray-600 max-h-28 overflow-y-auto">
            <code>{step.api?.sample}</code>
          </pre>
        </div>
      </div>
    </div>
  );
};
