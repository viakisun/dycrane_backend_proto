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

export interface Log {
  time: string;
  actor: string;
  summary: string;
  isError?: boolean;
};

export type StepStatus = 'idle' | 'in-progress' | 'done' | 'error';

export type WorkflowContext = {
  [key: string]: any;
};

const TEST_USERS = {
    SAFETY_MANAGER: { id: "user-safety-manager-01", token: "dummy-token-sm", orgId: "org-safety-01" },
    MANUFACTURER: { id: "user-manufacturer-01", token: "dummy-token-mfr", orgId: "org-manufacturer-01" },
    OWNER: { id: "user-owner-01", token: "dummy-token-own", orgId: "org-owner-01" },
    DRIVER: { id: "user-driver-01", token: "dummy-token-drv", orgId: "org-owner-01" },
};

type WorkflowState = {
  logsByStepCode: Record<string, Log[]>;
  stepStatus: Record<string, StepStatus>;
  error: string | null;
  isRunning: boolean;
  context: WorkflowContext;
  actions: {
    runStep: (stepCode: string) => Promise<void>;
    runAllSteps: () => Promise<void>;
    addLog: (stepCode: string, log: Omit<Log, 'time'>) => void;
    clearLogs: (stepCode: string) => void;
    fullReset: () => Promise<void>;
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
  logsByStepCode: {},
  stepStatus: WORKFLOW_STEPS.reduce((acc, step) => ({ ...acc, [step.code]: 'idle' }), {}),
  error: null,
  isRunning: false,
  context: { users: TEST_USERS },
};

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  ...initialState,
  actions: {
    addLog: (stepCode, log) => {
        set(state => ({
            logsByStepCode: {
                ...state.logsByStepCode,
                [stepCode]: [
                    ...(state.logsByStepCode[stepCode] || []),
                    { ...log, time: new Date().toLocaleTimeString() }
                ]
            }
        }));
    },
    clearLogs: (stepCode) => {
        set(state => ({
            logsByStepCode: { ...state.logsByStepCode, [stepCode]: [] }
        }));
    },
    fullReset: async () => {
        get().actions.addLog('A1', { actor: 'SYSTEM', summary: 'Resetting server state...' });
        try {
            await apiAdapter.post('SYSTEM', '/health/reset-transactional');
            set(initialState);
            get().actions.addLog('A1', { actor: 'SYSTEM', summary: 'Server and client state reset successfully.' });
        } catch (error: any) {
            get().actions.addLog('A1', { actor: 'SYSTEM', summary: `Error resetting server state: ${error.message}`, isError: true });
        }
    },
    runStep: async (stepCode: string) => {
      const { context, actions } = get();
      const stepInfo = WORKFLOW_STEPS.find(s => s.code === stepCode);
      if (!stepInfo) return;

      actions.clearLogs(stepCode);
      set(state => ({ stepStatus: { ...state.stepStatus, [stepCode]: 'in-progress' } }));
      actions.addLog(stepCode, { actor: stepInfo.actor, summary: `${stepInfo.title} started.` });

      try {
        const stepFn = stepFunctions[stepCode];
        if (stepFn) {
          const stepInput = { ...context, context, actions, stepCode };
          const result = await stepFn(stepInput);
          if (result) {
            const newContext = { ...get().context, ...result };
            set({ context: newContext });
            actions.addLog(stepCode, { actor: 'SYSTEM', summary: `Context updated: ${JSON.stringify(result)}` });
          }
        }

        actions.addLog(stepCode, { actor: 'SYSTEM', summary: 'Step completed successfully.' });
        set(state => ({ stepStatus: { ...state.stepStatus, [stepCode]: 'done' } }));
      } catch (error: any) {
        actions.addLog(stepCode, { actor: 'SYSTEM', summary: `Error: ${error.message}`, isError: true });
        set(state => ({
            stepStatus: { ...state.stepStatus, [stepCode]: 'error' },
            error: error.message
        }));
      }
    },
    runAllSteps: async () => {
        set({ isRunning: true, error: null });
        const { actions } = get();

        for (const step of WORKFLOW_STEPS) {
            if (get().error) {
                // This log needs a home. Maybe a general log? For now, console.log.
                console.error('Workflow aborted due to error.');
                break;
            }
            if (stepFunctions[step.code]) {
                await actions.runStep(step.code);
            }
        }
        set({ isRunning: false });
    },
  },
}));
