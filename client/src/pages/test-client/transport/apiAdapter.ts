import apiClient from '../../../apiClient';
import { useWorkflowStore, WorkflowContext } from '../state/workflowStore';
import { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1s

type Actor = keyof NonNullable<WorkflowContext['users']>;

// A wrapper to get the current state from the Zustand store outside of a React component
const { getState } = useWorkflowStore;

async function request<T>(
  actor: Actor,
  config: AxiosRequestConfig
): Promise<AxiosResponse<T>> {
  const { context, actions } = getState();
  const user = context.users?.[actor];

  if (!user?.token) {
    throw new Error(`No token found for actor: ${actor}`);
  }

  const headers = {
    ...config.headers,
    Authorization: `Bearer ${user.token}`,
    'X-User-ID': user.id,
    'X-Org-ID': user.orgId || '',
  };

  const requestConfig: AxiosRequestConfig = {
    ...config,
    headers
  };

  actions.addLog({
    actor,
    stepCode: 'API_REQUEST',
    summary: `Request: ${config.method?.toUpperCase()} ${config.url}`,
    type: 'request',
    forwarded: {
        data: config.data
    }
  });

  for (let i = 0; i < MAX_RETRIES; i++) {
    try {
      const response = await apiClient.request<T>(requestConfig);
      actions.addLog({
        actor,
        stepCode: 'API_RESPONSE',
        summary: `Success: ${response.status} ${config.url}`,
        type: 'response',
        extracted: {
            data: response.data
        }
      });
      return response;
    } catch (error) {
      const axiosError = error as AxiosError;
      actions.addLog({
          actor,
          stepCode: 'API_ERROR',
          summary: `Attempt ${i + 1} failed for ${config.url}: ${axiosError.message}`,
          type: 'error',
          extracted: {
            status: axiosError.response?.status,
            data: axiosError.response?.data,
          }
      });

      if (i === MAX_RETRIES - 1) {
        throw new Error(`API request failed after ${MAX_RETRIES} retries: ${axiosError.message}`);
      }
      await new Promise(res => setTimeout(res, RETRY_DELAY));
    }
  }
  // This line should be unreachable
  throw new Error('API request failed unexpectedly.');
}

export const apiAdapter = {
  get: <T>(actor: Actor, url: string, config?: AxiosRequestConfig) =>
    request<T>(actor, { ...config, method: 'GET', url }),
  post: <T>(actor: Actor, url: string, data?: any, config?: AxiosRequestConfig) =>
    request<T>(actor, { ...config, method: 'POST', url, data }),
  put: <T>(actor: Actor, url: string, data?: any, config?: AxiosRequestConfig) =>
    request<T>(actor, { ...config, method: 'PUT', url, data }),
  delete: <T>(actor: Actor, url: string, config?: AxiosRequestConfig) =>
    request<T>(actor, { ...config, method: 'DELETE', url }),
};
