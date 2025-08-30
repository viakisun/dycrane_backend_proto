import { useWorkflowStore, WorkflowContext } from '../state/workflowStore';

export type Step<TInput, TOutput> = (
  input: TInput
) => Promise<TOutput>;

export type StepInput = {
  context: WorkflowContext;
  actions: ReturnType<typeof useWorkflowStore.getState>['actions'];
};

export const runStep = async <TOutput>(
    stepCode: string,
    stepFn: () => Promise<TOutput>
): Promise<TOutput> => {
    const { actions } = useWorkflowStore.getState();
    actions.setCurrentStep(stepCode);
    actions.setStepStatus(stepCode, 'running');

    try {
        const result = await stepFn();
        actions.setStepStatus(stepCode, 'success');
        actions.addLog({
            actor: 'SYSTEM',
            stepCode,
            summary: `Step successful: ${stepCode}`,
            type: 'success',
            extracted: result,
        });
        return result;
    } catch (error: any) {
        actions.setStepStatus(stepCode, 'error');
        actions.setError(`Error in step ${stepCode}: ${error.message}`);
        actions.addLog({
            actor: 'SYSTEM',
            stepCode,
            summary: `Step failed: ${stepCode}`,
            type: 'error',
            extracted: { message: error.message },
        });
        throw error;
    } finally {
        actions.setCurrentStep(null);
    }
};
