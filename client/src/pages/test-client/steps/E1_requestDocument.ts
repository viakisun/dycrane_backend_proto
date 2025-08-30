import { apiAdapter } from '../transport/apiAdapter';
import { StepInput, runStep } from './types';

type RequestDocumentInput = StepInput & {
  siteId: string;
};

type RequestDocumentOutput = {
    docRequestId: string;
};

export async function requestDocument(input: RequestDocumentInput): Promise<RequestDocumentOutput> {
  return runStep('E1.requestDocument', async () => {
    const { context, siteId } = input;
    const safetyManager = context.users?.SAFETY_MANAGER;
    const driver = context.users?.DRIVER;

    if (!safetyManager) throw new Error('Safety manager not found in context');
    if (!driver) throw new Error('Driver not found in context');
    if (!siteId) throw new Error('siteId is required');

    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + 90);

    const docRequestData = {
        site_id: siteId,
        driver_id: driver.id,
        requested_by_id: safetyManager.id,
        due_date: dueDate.toISOString().split('T')[0],
    };

    const response = await apiAdapter.post('SAFETY_MANAGER', '/docs/requests', docRequestData);
    const docRequestId = response.data.request_id;

    if (!docRequestId) {
        throw new Error('Failed to get docRequestId from response');
    }

    return { docRequestId };
  });
}
