import React from 'react';
import { ControlPanel } from './test-client/ui/ControlPanel';
import { LogPanel } from './test-client/ui/LogPanel';
import { Notification } from './test-client/ui/Notification';
import { WorkflowRail } from './test-client/ui/WorkflowRail';
import { runMainWorkflow } from './test-client/actors/mainWorkflow';

const WORKFLOW_STEPS = [
    { code: 'B1.createSite', name: 'B1. 현장 생성 (안전관리자)' },
    { code: 'B2.approveSite', name: 'B2. 현장 승인 (제조사)' },
    { code: 'C1.listOwnerCranes', name: 'C1. 크레인 목록 조회 (사업주)' },
    { code: 'C3.requestCraneAssignment', name: 'C3. 크레인 배치 요청 (안전관리자)' },
    { code: 'D1.assignDriver', name: 'D1. 운전자 배정 (사업주)' },
    { code: 'D2.recordAttendance', name: 'D2. 출근 기록 (운전자)' },
    { code: 'E1.requestDocument', name: 'E1. 서류 요청 (안전관리자)' },
    { code: 'E2.submitDocument', name: 'E2. 서류 제출 (운전자)' },
    { code: 'E3.reviewDocument', name: 'E3. 서류 검토 (안전관리자)' },
];

const TestClientPage: React.FC = () => {
    const handleRunWorkflow = () => {
        // This is now an async call, but we don't need to await it here
        // as the UI will react to the state changes from the store.
        runMainWorkflow();
    };

    return (
        <>
            <Notification />
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 p-4">
                <div className="lg:col-span-1">
                    <WorkflowRail steps={WORKFLOW_STEPS} />
                </div>
                <div className="lg:col-span-3 flex flex-col gap-8">
                    <ControlPanel onRunWorkflow={handleRunWorkflow} />
                    <LogPanel />
                </div>
            </div>
        </>
    );
};

export default TestClientPage;
