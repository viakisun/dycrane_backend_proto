import { apiAdapter } from '../transport/apiAdapter';
import { StepInput, runStep } from './types';

type RequestCraneInput = StepInput & {
  siteId: string;
  craneId: string;
};

type RequestCraneOutput = {
    assignmentId: string;
};

export async function requestCraneAssignment(input: RequestCraneInput): Promise<RequestCraneOutput> {
  return runStep('C3.requestCraneAssignment', async () => {
    const { context, siteId, craneId } = input;
    const safetyManager = context.users?.SAFETY_MANAGER;

    if (!safetyManager) throw new Error('Safety manager not found in context');
    if (!siteId) throw new Error('siteId is required');
    if (!craneId) throw new Error('craneId is required');

    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 30);
    const endDate = new Date(startDate);
    endDate.setDate(startDate.getDate() + 90);

    const assignCraneData = {
        site_id: siteId,
        crane_id: craneId,
        safety_manager_id: safetyManager.id,
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
    };

    const response = await apiAdapter.post('SAFETY_MANAGER', '/assignments/crane', assignCraneData);
    const assignmentId = response.data.assignment_id;

    if (!assignmentId) {
        throw new Error('Failed to get assignmentId from response');
    }

    return { assignmentId };
  });
}
