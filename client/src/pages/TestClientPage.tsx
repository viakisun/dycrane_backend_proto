import React, { useEffect } from 'react';
import StepPanel from './test-client/ui/StepPanel';
import LogConsole from './test-client/ui/LogConsole';
import WorkflowRail from './test-client/ui/WorkflowRail';
import { useWorkflowStore } from './test-client/state/workflowStore';

const TestClientPage: React.FC = () => {
  const { initialize } = useWorkflowStore(state => state.actions);

  useEffect(() => {
    initialize();
  }, [initialize]);

  return (
    <div className="bg-gray-900 min-h-screen text-white font-mono p-4">
      <header className="mb-4">
        <h1 className="text-2xl font-bold">Test Client – Developer Guide</h1>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
        <div className="md:col-span-3">
          <WorkflowRail />
        </div>
        <div className="md:col-span-5">
          <StepPanel />
        </div>
        <div className="md:col-span-4">
          <LogConsole />
        </div>
      </div>
      <footer className="text-center text-xs text-gray-600 mt-4">
        <p>Commit: abc1234 | Version: 0.1.0</p>
      </footer>
    </div>
  );
};

export default TestClientPage;
