import { apiAdapter } from '../transport/apiAdapter';
import { StepInput, runStep } from './types';

type ReviewDocumentInput = StepInput & {
  docItemId: string;
};

export async function reviewDocument(input: ReviewDocumentInput): Promise<{}> {
  return runStep('E3.reviewDocument', async () => {
    const { context, docItemId } = input;
    const safetyManager = context.users?.SAFETY_MANAGER;

    if (!safetyManager) throw new Error('Safety manager not found in context');
    if (!docItemId) throw new Error('docItemId is required');

    const docReviewData = {
        item_id: docItemId,
        reviewer_id: safetyManager.id,
        approve: true
    };

    await apiAdapter.post('SAFETY_MANAGER', '/docs/items/review', docReviewData);

    return {};
  });
}
