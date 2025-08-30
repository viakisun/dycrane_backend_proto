import { useWorkflowStore } from '../state/workflowStore';
import { createSite } from '../steps/B1_createSite';
import { approveSite } from '../steps/B2_approveSite';
import { listOwnerCranes } from '../steps/C1_listOwnerCranes';
import { requestCraneAssignment } from '../steps/C3_requestCraneAssignment';
import { assignDriver } from '../steps/D1_assignDriver';
import { recordAttendance } from '../steps/D2_recordAttendance';
import { requestDocument } from '../steps/E1_requestDocument';
import { submitDocument } from '../steps/E2_submitDocument';
import { reviewDocument } from '../steps/E3_reviewDocument';

export async function runMainWorkflow() {
    const { actions, context } = useWorkflowStore.getState();

    try {
        const stepInput = { context, actions };

        const { siteId } = await createSite(stepInput);
        actions.updateContext({ siteId });

        await approveSite({ ...stepInput, siteId });

        const { craneId } = await listOwnerCranes(stepInput);
        actions.updateContext({ craneId });

        const { assignmentId } = await requestCraneAssignment({ ...stepInput, siteId, craneId });
        actions.updateContext({ assignmentId });

        const { driverAssignmentId } = await assignDriver({ ...stepInput, assignmentId });
        actions.updateContext({ driverAssignmentId });

        await recordAttendance({ ...stepInput, driverAssignmentId });

        const { docRequestId } = await requestDocument({ ...stepInput, siteId });
        actions.updateContext({ docRequestId });

        const { docItemId } = await submitDocument({ ...stepInput, docRequestId });
        actions.updateContext({ docItemId });

        await reviewDocument({ ...stepInput, docItemId });

        actions.addLog({
            actor: 'SYSTEM',
            stepCode: 'WORKFLOW_COMPLETE',
            summary: 'E2E workflow completed successfully.',
            type: 'success',
        });

    } catch (error: any) {
        actions.setError(`Workflow failed: ${error.message}`);
        actions.addLog({
            actor: 'SYSTEM',
            stepCode: 'WORKFLOW_FAILED',
            summary: 'E2E workflow stopped due to an error.',
            type: 'error',
        });
    } finally {
        actions.finishWorkflow();
    }
}
