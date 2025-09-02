import { apiAdapter } from '../transport/apiAdapter';
import { StepInput } from './types';

// NOTE: The server-side implementation of login is NOT part of this commit.
// This client-side code assumes that a dev-mode login endpoint exists
// that assigns roles based on email prefixes.
const USERS_TO_LOGIN = [
  { role: 'SAFETY_MANAGER', email: 'safety@example.com' },
  { role: 'OWNER', email: 'owner@example.com' },
  { role: 'DRIVER', email: 'driver@example.com' },
  { role: 'MANUFACTURER', email: 'manufacturer@example.com' },
];

type UserProfile = {
  id: string;
  email: string;
  name: string;
  roles: string[];
  token: string;
  orgId?: string;
};

type PrepareSessionsOutput = {
  users: Record<string, UserProfile>;
};

export async function prepareSessions(input: StepInput): Promise<PrepareSessionsOutput> {
  const userProfiles: Record<string, UserProfile> = {};

  for (const user of USERS_TO_LOGIN) {
    const response = await apiAdapter.post(
      'SYSTEM', // Login does not require a token
      '/auth/login',
      {
        email: user.email,
        password: 'password_is_ignored_in_dev_mode',
      }
    );

    const { access_token, user: userData } = response.data;

    if (!access_token || !userData) {
      throw new Error(`Login failed for role ${user.role}: Invalid response data`);
    }

    userProfiles[user.role] = {
      ...userData,
      token: access_token,
      orgId: user.role === 'OWNER' ? 'org-owner-01' : undefined,
    };
  }

  return { users: userProfiles };
}
