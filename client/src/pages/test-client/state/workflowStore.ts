import { create } from 'zustand';

// As per work order: `time, actor, stepCode, summary, extracted, forwarded`
export type LogEntry = {
  time: string;
  actor: string;
  stepCode: string;
  summary: string;
  extracted?: Record<string, any>;
  forwarded?: Record<string, any>;
  type: 'info' | 'error' | 'success' | 'request' | 'response';
};

export type StepStatus = 'pending' | 'success' | 'error' | 'running';

// Shared context for data passing between steps
export type WorkflowContext = {
  // Runtime config
  host?: string;
  port?: number;
  users?: Record<string, { token: string, id: string, orgId?: string }>;

  // Data extracted from steps
  siteId?: string;
  craneId?: string;
  assignmentId?: string;
  driverAssignmentId?: string;
  docRequestId?: string;
  docItemId?: string;

  [key: string]: any; // Allow flexible data storage
};

type WorkflowState = {
  logs: LogEntry[];
  stepStatus: Record<string, StepStatus>;
  currentStep: string | null;
  error: string | null;
  isRunning: boolean;
  context: WorkflowContext;
  actions: {
    startWorkflow: (config: Pick<WorkflowContext, 'host' | 'port' | 'users'>) => void;
    finishWorkflow: () => void;
    reset: () => void;
    addLog: (log: Omit<LogEntry, 'time'>) => void;
    setStepStatus: (stepCode: string, status: StepStatus) => void;
    setCurrentStep: (stepCode: string | null) => void;
    setError: (error: string | null) => void;
    updateContext: (data: Partial<WorkflowContext>) => void;
  };
};

const initialState = {
    logs: [],
    stepStatus: {},
    currentStep: null,
    error: null,
    isRunning: false,
    context: {},
};

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  ...initialState,
  actions: {
    startWorkflow: (config) => set({
        isRunning: true,
        error: null,
        logs: [],
        stepStatus: {},
        currentStep: null,
        context: { ...initialState.context, ...config },
    }),
    finishWorkflow: () => set({ isRunning: false, currentStep: null }),
    reset: () => set(initialState),
    addLog: (log) => set((state) => ({
        logs: [...state.logs, { ...log, time: new Date().toISOString() }],
    })),
    setStepStatus: (stepCode, status) => set((state) => ({
        stepStatus: { ...state.stepStatus, [stepCode]: status },
    })),
    setCurrentStep: (stepCode) => set({ currentStep: stepCode }),
    setError: (error) => set({ error }),
    updateContext: (data) => set((state) => ({
        context: { ...state.context, ...data },
    })),
  },
}));
