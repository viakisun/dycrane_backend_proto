import { apiAdapter } from '../transport/apiAdapter';
import { StepInput } from './types';

type ApproveSiteInput = StepInput & {
  siteId: string;
};

export async function approveSite(input: ApproveSiteInput): Promise<void> {
  const { context, siteId } = input;
  const manufacturer = context.users?.MANUFACTURER;

  if (!manufacturer) {
    throw new Error('Manufacturer not found in context');
  }

  const approveData = {
    approved_by_id: manufacturer.id,
  };

  await apiAdapter.post('MANUFACTURER', `/sites/${siteId}/approve`, approveData);
}
