import { apiAdapter } from '../transport/apiAdapter';
import { StepInput, runStep } from './types';

type ListCranesOutput = {
  craneId: string;
};

export async function listOwnerCranes(input: StepInput): Promise<ListCranesOutput> {
  return runStep('C1.listOwnerCranes', async () => {
    const { context } = input;
    const owner = context.users?.OWNER;

    if (!owner?.orgId) {
      throw new Error('Owner or owner organization ID not found in context');
    }

    const response = await apiAdapter.get('OWNER', `/owners/${owner.orgId}/cranes`);
    const craneId = response.data[0]?.id;

    if (!craneId) {
      throw new Error('No available cranes found for owner');
    }

    return { craneId };
  });
}
