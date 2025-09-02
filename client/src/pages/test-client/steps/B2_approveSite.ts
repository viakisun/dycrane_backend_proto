import { apiAdapter } from '../transport/apiAdapter';
import { StepInput } from './types';
import { SiteStatus } from './enums';

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
    status: SiteStatus.ACTIVE,
    approved_by_id: manufacturer.id,
  };

  await apiAdapter.patch('MANUFACTURER', `/org/sites/${siteId}`, approveData);
}
