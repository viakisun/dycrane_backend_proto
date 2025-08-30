import { apiAdapter } from '../transport/apiAdapter';
import { StepInput, runStep } from './types';

type CreateSiteOutput = {
  siteId: string;
};

export async function createSite(input: StepInput): Promise<CreateSiteOutput> {
  return runStep('B1.createSite', async () => {
    const { context } = input;
    const safetyManager = context.users?.SAFETY_MANAGER;

    if (!safetyManager) {
      throw new Error('Safety manager not found in context');
    }

    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 30);
    const endDate = new Date(startDate);
    endDate.setDate(startDate.getDate() + 90);

    const siteData = {
      name: `E2E Test Site - ${new Date().toISOString()}`,
      address: '123 Test Street, Test City',
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0],
      requested_by_id: safetyManager.id,
    };

    const response = await apiAdapter.post('SAFETY_MANAGER', '/sites/', siteData);
    const siteId = response.data.id;

    if (!siteId) {
      throw new Error('Failed to get siteId from response');
    }

    return { siteId };
  });
}
