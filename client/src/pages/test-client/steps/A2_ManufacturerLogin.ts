import { apiAdapter } from '../transport/apiAdapter';
import { StepInput, StepOutput } from './types';

const USER_ROLE = 'MANUFACTURER';
const USER_EMAIL = 'mfr1@example.com';

export async function manufacturerLogin(input: StepInput): Promise<StepOutput> {
  const { addLog } = input.actions;

  addLog(input.stepCode, {
    actor: USER_ROLE,
    summary: `Requesting token for ${USER_ROLE} (${USER_EMAIL})`,
  });

  const response = await apiAdapter.post(
    'SYSTEM', // Login does not require an existing token
    '/auth/login',
    {
      email: USER_EMAIL,
      password: 'password',
    }
  );

  const { access_token, user } = response.data;

  if (!access_token || !user) {
    throw new Error(`Login failed for role ${USER_ROLE}: Invalid response data`);
  }

  addLog(input.stepCode, {
    actor: USER_ROLE,
    summary: `Login successful. Token received.`,
  });

  // Return a partial context that will be merged into the main context
  return {
    users: {
      ...input.context.users,
      [USER_ROLE]: {
        ...user,
        token: access_token,
      },
    },
  };
}
