import { apiAdapter } from '../transport/apiAdapter';
import { StepInput } from './types';

type ApproveRequestInput = StepInput & {
  assignmentId: string; // This is the request_id from the previous step
};

export async function approveRequest(input: ApproveRequestInput): Promise<void> {
  const { context, assignmentId } = input;
  const owner = context.users?.OWNER;

  if (!owner) {
    throw new Error('Owner not found in context');
  }

  if (!assignmentId) {
      throw new Error('assignmentId (request_id) not found in context for C5');
  }

  const approveData = {
    status: 'APPROVED',
    approver_id: owner.id,
    notes: 'Approved via test client',
  };

  await apiAdapter.post('OWNER', `/requests/${assignmentId}/respond`, approveData);
}
