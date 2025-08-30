import { apiAdapter } from '../transport/apiAdapter';
import { StepInput, runStep } from './types';

type SubmitDocumentInput = StepInput & {
  docRequestId: string;
};

type SubmitDocumentOutput = {
    docItemId: string;
};

export async function submitDocument(input: SubmitDocumentInput): Promise<SubmitDocumentOutput> {
  return runStep('E2.submitDocument', async () => {
    const { docRequestId } = input;
    if (!docRequestId) throw new Error('docRequestId is required');

    const docSubmitData = {
        request_id: docRequestId,
        doc_type: "Safety Certificate",
        file_url: "https://example.com/safety-cert.pdf"
    };

    const response = await apiAdapter.post('DRIVER', '/docs/items/submit', docSubmitData);
    const docItemId = response.data.item_id;

    if (!docItemId) {
        throw new Error('Failed to get docItemId from response');
    }

    return { docItemId };
  });
}
