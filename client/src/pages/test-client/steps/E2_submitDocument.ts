import { apiAdapter } from '../transport/apiAdapter';
import { StepInput } from './types';

type SubmitDocumentInput = StepInput & {
  docRequestId: string;
};

type SubmitDocumentOutput = {
  docItemId: string;
};

export async function submitDocument(
  input: SubmitDocumentInput
): Promise<SubmitDocumentOutput> {
  const { actions, docRequestId } = input;

  actions.addLog({
    actor: 'DEBUG',
    stepCode: 'E2',
    summary: `Submitting document for request ID: ${docRequestId}`,
  });

  if (!docRequestId) {
    throw new Error('docRequestId is missing for submitDocument step');
  }

  const docSubmitData = {
    request_id: docRequestId,
    doc_type: 'Safety Certificate',
    file_url: 'https://example.com/safety-cert.pdf',
  };

  const response = await apiAdapter.post(
    'DRIVER',
    '/docs/items/submit',
    docSubmitData
  );

  const docItemId = response.data.item_id;

  if (!docItemId) {
    throw new Error('Failed to get docItemId from response');
  }

  return { docItemId };
}
