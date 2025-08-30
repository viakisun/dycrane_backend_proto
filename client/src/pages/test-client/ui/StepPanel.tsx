import React, { useState } from 'react';
import { useWorkflowStore } from '../state/workflowStore';
import { WORKFLOW_STEPS } from '../workflow-def';

const StepPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState('description');
  const { selectedStep: selectedStepCode } = useWorkflowStore();
  const selectedStep = WORKFLOW_STEPS.find(step => step.code === selectedStepCode) || WORKFLOW_STEPS[0];

  return (
    <div className="bg-gray-800 text-white p-4 rounded-lg">
      <div className="flex border-b border-gray-700">
        <button
          className={`px-4 py-2 ${activeTab === 'description' ? 'border-b-2 border-blue-500' : ''}`}
          onClick={() => setActiveTab('description')}
        >
          Description
        </button>
        <button
          className={`px-4 py-2 ${activeTab === 'data-flow' ? 'border-b-2 border-blue-500' : ''}`}
          onClick={() => setActiveTab('data-flow')}
        >
          Data Flow
        </button>
        <button
          className={`px-4 py-2 ${activeTab === 'notes' ? 'border-b-2 border-blue-500' : ''}`}
          onClick={() => setActiveTab('notes')}
        >
          Notes
        </button>
      </div>
      <div className="pt-4">
        {activeTab === 'description' && (
          <div>
            <h3 className="text-lg font-bold">{selectedStep.title}</h3>
            <p className="text-sm text-gray-400">Actor: {selectedStep.actor}</p>
            <p className="mt-4">{selectedStep.description}</p>
          </div>
        )}
        {activeTab === 'data-flow' && (
          <div>
            <h4 className="font-bold">In</h4>
            <pre className="bg-gray-900 p-2 rounded mt-2">
              <code>{selectedStep.dataFlow.in.join('\n')}</code>
            </pre>
            <h4 className="font-bold mt-4">Out</h4>
            <pre className="bg-gray-900 p-2 rounded mt-2">
              <code>{selectedStep.dataFlow.out.join('\n')}</code>
            </pre>
            <p className="text-sm text-gray-500 mt-4">
              * Note: `request/response/assert` details are implemented in the code but not displayed here.
            </p>
          </div>
        )}
        {activeTab === 'notes' && (
          <div>
            <textarea
              className="w-full h-40 bg-gray-900 text-white p-2 rounded"
              placeholder="Developer notes..."
            ></textarea>
          </div>
        )}
      </div>
    </div>
  );
};

export default StepPanel;
