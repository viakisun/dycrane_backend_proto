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

  const response = await apiAdapter.get('OWNER', `/owners/${owner.orgId}/cranes`);
  const cranes = response.data;

  if (!cranes || cranes.length === 0) {
    throw new Error('No cranes found for owner');
  }

  return { craneId: cranes[0].id };
}
