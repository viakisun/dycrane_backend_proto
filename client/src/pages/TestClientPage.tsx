import React, { useEffect } from 'react';
import StepPanel from './test-client/ui/StepPanel';
import LogConsole from './test-client/ui/LogConsole';
import WorkflowRail from './test-client/ui/WorkflowRail';
import { useWorkflowStore } from './test-client/state/workflowStore';

const TestClientPage: React.FC = () => {
  const { initialize, reset } = useWorkflowStore(state => state.actions);

  useEffect(() => {
    reset();
    initialize();
  }, [initialize, reset]);

  return (
    <div className="min-h-screen p-4">
      <header className="mb-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-300">Test Client – Developer Guide</h1>
        <p className="text-xs text-gray-500">Commit: abc1234 | Version: 0.1.0</p>
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
