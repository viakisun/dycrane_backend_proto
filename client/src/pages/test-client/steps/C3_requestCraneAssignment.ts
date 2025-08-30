import { apiAdapter } from '../transport/apiAdapter';
import { StepInput } from './types';

type RequestCraneAssignmentInput = StepInput & {
  siteId: string;
  craneId: string;
};

type RequestCraneAssignmentOutput = {
  assignmentId: string;
};

export async function requestCraneAssignment(
  input: RequestCraneAssignmentInput
): Promise<RequestCraneAssignmentOutput> {
  const { context, siteId, craneId } = input;
  const safetyManager = context.users?.SAFETY_MANAGER;

  if (!safetyManager) {
    throw new Error('Safety manager not found in context');
  }

  const startDate = new Date();
  startDate.setDate(startDate.getDate() + 30);
  const endDate = new Date(startDate);
  endDate.setDate(startDate.getDate() + 90);

  const assignmentData = {
    site_id: siteId,
    crane_id: craneId,
    safety_manager_id: safetyManager.id,
    start_date: startDate.toISOString().split('T')[0],
    end_date: endDate.toISOString().split('T')[0],
  };

  const response = await apiAdapter.post(
    'SAFETY_MANAGER',
    '/assignments/crane',
    assignmentData
  );

  const assignmentId = response.data.assignment_id;

  if (!assignmentId) {
    throw new Error('Failed to get assignmentId from response');
  }

  return { assignmentId };
}
