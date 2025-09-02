import { apiAdapter } from '../transport/apiAdapter';
import { StepInput } from './types';

type ReviewDocumentInput = StepInput & {
  docItemId: string;
};

export async function reviewDocument(input: ReviewDocumentInput): Promise<void> {
  const { context, docItemId } = input;
  const safetyManager = context.users?.SAFETY_MANAGER;

  if (!safetyManager) {
    throw new Error('Safety manager not found in context');
  }

  const docReviewData = {
    item_id: docItemId,
    reviewer_id: safetyManager.id,
    approve: true,
  };

  await apiAdapter.post(
    'SAFETY_MANAGER',
    `/compliance/document-items/${docItemId}/review`,
    docReviewData
  );
}
