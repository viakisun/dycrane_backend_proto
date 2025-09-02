import { apiAdapter } from '../transport/apiAdapter';
import { StepInput } from './types';

type RequestDocumentInput = StepInput & {
  siteId: string;
};

type RequestDocumentOutput = {
  docRequestId: string;
};

export async function requestDocument(
  input: RequestDocumentInput
): Promise<RequestDocumentOutput> {
  const { context, siteId } = input;
  const safetyManager = context.users?.SAFETY_MANAGER;
  const driver = context.users?.DRIVER;

  if (!safetyManager || !driver) {
    throw new Error('Safety manager or driver not found in context');
  }

  const endDate = new Date();
  endDate.setDate(endDate.getDate() + 90);

  const docRequestData = {
    site_id: siteId,
    driver_id: driver.id,
    requested_by_id: safetyManager.id,
    due_date: endDate.toISOString().split('T')[0],
  };

  const response = await apiAdapter.post(
    'SAFETY_MANAGER',
    '/compliance/document-requests',
    docRequestData
  );

  const docRequestId = response.data.request_id;

  if (!docRequestId) {
    throw new Error('Failed to get docRequestId from response');
  }

  return { docRequestId };
}
