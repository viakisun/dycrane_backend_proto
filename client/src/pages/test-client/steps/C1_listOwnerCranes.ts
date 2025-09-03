import { apiAdapter } from '../transport/apiAdapter';
import { StepInput } from './types';

type ListOwnerCranesOutput = {
  craneId: string;
};

export async function listOwnerCranes(input: StepInput): Promise<ListOwnerCranesOutput> {
  const { context } = input;
  const owner = context.users?.OWNER;

  if (!owner) {
    throw new Error('Owner not found in context');
  }

  const response = await apiAdapter.get('OWNER', `/org/owners/${owner.orgId}/cranes?status=NORMAL`);
  const cranes = response.data;

  if (!cranes || cranes.length === 0) {
    throw new Error('No available cranes found for owner');
  }

  // Return the first available crane
  return { craneId: cranes[0].id };
}
