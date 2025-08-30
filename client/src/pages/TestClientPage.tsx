import React, { useEffect } from 'react';
import StepPanel from './test-client/ui/StepPanel';
import LogConsole from './test-client/ui/LogConsole';
import WorkflowRail from './test-client/ui/WorkflowRail';
import { useWorkflowStore } from './test-client/state/workflowStore';

const TestClientPage: React.FC = () => {
  const { initialize, reset } = useWorkflowStore(state => state.actions);

  useEffect(() => {
    // Initialize the context with user data on first load
    initialize();
  }, [initialize]);

  const handleReset = () => {
    // This will now call the server to reset the DB and then reset the client state
    reset();
  };

  return (
    <div className="min-h-screen p-4">
      <header className="mb-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-300">Test Client – Developer Guide</h1>
        <div className="flex items-center space-x-4">
            <button
                onClick={handleReset}
                className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition-colors duration-150"
            >
                Reset Server State
            </button>
            <p className="text-xs text-gray-500">Commit: abc1234 | Version: 0.1.0</p>
        </div>
      </header>
      <main className="grid grid-cols-1 lg:grid-cols-12 gap-4">
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
