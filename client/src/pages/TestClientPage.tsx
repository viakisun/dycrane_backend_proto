import React, { useEffect } from 'react';
import StepPanel from './test-client/ui/StepPanel';
import LogConsole from './test-client/ui/LogConsole';
import WorkflowRail from './test-client/ui/WorkflowRail';
import { useWorkflowStore } from './test-client/state/workflowStore';

const TestClientPage: React.FC = () => {
  const { initialize, reset } = useWorkflowStore(state => state.actions);

  useEffect(() => {
    initialize();
  }, [initialize]);

  const handleReset = () => {
    reset();
  };

  return (
    <div className="min-h-screen p-4 md:p-6 lg:p-8">
      <header className="mb-6 flex justify-between items-center">
        <div>
            <h1 className="text-2xl font-bold text-gray-800">Developer Guide</h1>
            <p className="text-sm text-gray-500">Interactive E2E Workflow Test Client</p>
        </div>
        <div className="flex items-center space-x-4">
            <button
                onClick={handleReset}
                className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded transition-colors duration-150"
            >
                Reset Workflow Data
            </button>
        </div>
      </header>
      <main className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-3">
          <WorkflowRail />
        </div>
        <div className="lg:col-span-5">
          <StepPanel />
        </div>
        <div className="lg:col-span-4">
          <LogConsole />
        </div>
      </main>
    </div>
  );
};

export default TestClientPage;
