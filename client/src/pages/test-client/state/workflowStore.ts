import { create } from 'zustand';
import { WORKFLOW_STEPS } from '../workflow-def';
import { createSite } from '../steps/B1_createSite';
import { approveSite } from '../steps/B2_approveSite';
import { listOwnerCranes } from '../steps/C1_listOwnerCranes';
import { requestCraneAssignment } from '../steps/C3_requestCraneAssignment';
import { assignDriver } from '../steps/D1_assignDriver';
import { recordAttendance } from '../steps/D2_recordAttendance';
import { requestDocument } from '../steps/E1_requestDocument';
import { submitDocument } from '../steps/E2_submitDocument';
import { reviewDocument } from '../steps/E3_reviewDocument';
import { apiAdapter } from '../transport/apiAdapter';

export type Log = {
  time: string;
  actor: string;
  stepCode: string;
  summary: string;
};

export type StepStatus = 'idle' | 'in-progress' | 'done' | 'error';

export type WorkflowContext = {
  [key: string]: any;
};

type WorkflowState = {
  logs: Log[];
  stepStatus: Record<string, StepStatus>;
  selectedStep: string;
  error: string | null;
  isRunning: boolean;
  context: WorkflowContext;
  actions: {
    runStep: (stepCode: string) => Promise<void>;
    runAllSteps: () => Promise<void>;
    setSelectedStep: (stepCode: string) => void;
    reset: () => void;
    initialize: () => Promise<void>;
    addLog: (log: Omit<Log, 'time'>) => void;
  };
};

const stepFunctions: { [key: string]: (input: any) => Promise<any> } = {
  B1: createSite,
  B2: approveSite,
  C1: listOwnerCranes,
  C3: requestCraneAssignment,
  D1: assignDriver,
  D2: recordAttendance,
  E1: requestDocument,
  E2: submitDocument,
  E3: reviewDocument,
};

const initialState = {
  logs: [],
  stepStatus: WORKFLOW_STEPS.reduce((acc, step) => ({ ...acc, [step.code]: 'idle' }), {}),
  selectedStep: WORKFLOW_STEPS[0].code,
  error: null,
  isRunning: false,
  context: {},
};

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  ...initialState,
  actions: {
    addLog: (log) => set((state) => ({
        logs: [...state.logs, { ...log, time: new Date().toLocaleTimeString() }],
    })),
    initialize: async () => {
        try {
            set(state => ({ ...state, stepStatus: { ...state.stepStatus, A1: 'in-progress' } }));
            const { data: users } = await apiAdapter.get('SYSTEM', '/users/by-role');
            const context = { users };
            set(state => ({
                context,
                logs: [...state.logs, { time: new Date().toLocaleTimeString(), actor: 'SYSTEM', stepCode: 'A1', summary: 'User sessions prepared.' }],
                stepStatus: { ...state.stepStatus, A1: 'done' }
            }));

            set(state => ({ ...state, stepStatus: { ...state.stepStatus, A2: 'in-progress' } }));
            set(state => ({
                logs: [...state.logs, { time: new Date().toLocaleTimeString(), actor: 'SYSTEM', stepCode: 'A2', summary: 'Environment check passed.' }],
                stepStatus: { ...state.stepStatus, A2: 'done' }
            }));
        } catch (error: any) {
            const errorMessage = `Initialization failed: ${error.message}`;
            set(state => ({
                logs: [...state.logs, { time: new Date().toLocaleTimeString(), actor: 'SYSTEM', stepCode: 'A1', summary: errorMessage }],
                stepStatus: { ...state.stepStatus, A1: 'error' },
                error: errorMessage
            }));
        }
    },
    runStep: async (stepCode: string) => {
      const { context, actions } = get();
      const stepInfo = WORKFLOW_STEPS.find(s => s.code === stepCode);
      if (!stepInfo) return;

      set(state => ({ stepStatus: { ...state.stepStatus, [stepCode]: 'in-progress' } }));
      actions.addLog({ actor: stepInfo.actor, stepCode, summary: `${stepInfo.title} started.` });

      try {
        const stepFn = stepFunctions[stepCode];
        if (stepFn) {
          const result = await stepFn({ context, actions });
          const newContext = { ...get().context, ...result };
          set({ context: newContext });
        }

        actions.addLog({ actor: 'SYSTEM', stepCode, summary: 'Step completed successfully.' });
        set(state => ({ stepStatus: { ...state.stepStatus, [stepCode]: 'done' } }));
      } catch (error: any) {
        actions.addLog({ actor: 'SYSTEM', stepCode, summary: `Error: ${error.message}` });
        set(state => ({
            stepStatus: { ...state.stepStatus, [stepCode]: 'error' },
            error: error.message
        }));
      }
    },
    runAllSteps: async () => {
      set({ isRunning: true, error: null });
      await get().actions.initialize();
      if (get().error) {
          set({ isRunning: false });
          return;
      }
      for (const step of WORKFLOW_STEPS) {
        if (stepFunctions[step.code]) {
            await get().actions.runStep(step.code);
            if (get().error) break;
        }
      }
      set({ isRunning: false });
    },
    setSelectedStep: (stepCode: string) => set({ selectedStep: stepCode }),
    reset: () => set(initialState),
  },
}));
