import { useWorkflowStore, WorkflowContext } from '../state/workflowStore';

export type Step<TInput, TOutput> = (
  input: TInput
) => Promise<TOutput>;

export type StepInput = {
  context: WorkflowContext;
  actions: ReturnType<typeof useWorkflowStore.getState>['actions'];
};
