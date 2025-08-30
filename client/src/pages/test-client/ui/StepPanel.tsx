import React, { useState } from 'react';
import { useWorkflowStore } from '../state/workflowStore';
import { WORKFLOW_STEPS } from '../workflow-def';

const StepPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState('description');
  const { selectedStep: selectedStepCode } = useWorkflowStore();
  const selectedStep = WORKFLOW_STEPS.find(step => step.code === selectedStepCode) || WORKFLOW_STEPS[0];

  const tabStyle = "px-4 py-2 text-sm font-medium transition-colors duration-150";
  const activeTabStyle = "border-b-2 border-blue-500 text-gray-800";
  const inactiveTabStyle = "text-gray-500 hover:bg-gray-100";

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm h-full border border-gray-200">
      <div className="flex border-b border-gray-200">
        <button
          className={`${tabStyle} ${activeTab === 'description' ? activeTabStyle : inactiveTabStyle}`}
          onClick={() => setActiveTab('description')}
        >
          Description
        </button>
        <button
          className={`${tabStyle} ${activeTab === 'data-flow' ? activeTabStyle : inactiveTabStyle}`}
          onClick={() => setActiveTab('data-flow')}
        >
          Data Flow
        </button>
        <button
          className={`${tabStyle} ${activeTab === 'notes' ? activeTabStyle : inactiveTabStyle}`}
          onClick={() => setActiveTab('notes')}
        >
          Notes
        </button>
      </div>
      <div className="pt-4 text-sm">
        {activeTab === 'description' && (
          <div className="space-y-3">
            <h3 className="text-lg font-bold text-gray-800">{selectedStep.title}</h3>
            <p className="text-xs text-gray-500">Actor: <span className="font-semibold text-blue-600">{selectedStep.actor}</span></p>
            <p className="text-gray-700 leading-relaxed">{selectedStep.description}</p>
          </div>
        )}
        {activeTab === 'data-flow' && (
          <div className="space-y-4">
            <div>
                <h4 className="font-bold text-gray-700">In (from context)</h4>
                <pre className="bg-gray-50 p-3 rounded mt-2 text-green-700 text-xs font-mono">
                  <code>{selectedStep.dataFlow.in.length > 0 ? selectedStep.dataFlow.in.join('\n') : 'N/A'}</code>
                </pre>
            </div>
            <div>
                <h4 className="font-bold text-gray-700">Out (to context)</h4>
                <pre className="bg-gray-50 p-3 rounded mt-2 text-orange-700 text-xs font-mono">
                  <code>{selectedStep.dataFlow.out.join('\n')}</code>
                </pre>
            </div>
            <p className="text-xs text-gray-400 mt-4 pt-4 border-t border-gray-200">
              * Note: `request/response/assert` details are implemented in the code but not displayed here.
            </p>
          </div>
        )}
        {activeTab === 'notes' && (
          <div>
            <textarea
              className="w-full h-60 bg-gray-50 text-gray-800 p-3 rounded text-sm border border-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="Developer notes for this step..."
            ></textarea>
          </div>
        )}
      </div>
    </div>
  );
};

export default StepPanel;
