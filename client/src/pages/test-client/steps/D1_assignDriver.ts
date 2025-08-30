import { apiAdapter } from '../transport/apiAdapter';
import { StepInput } from './types';

type AssignDriverInput = StepInput & {
  assignmentId: string;
};

type AssignDriverOutput = {
  driverAssignmentId: string;
};

export async function assignDriver(input: AssignDriverInput): Promise<AssignDriverOutput> {
  const { context, assignmentId } = input;
  const driver = context.users?.DRIVER;

  if (!driver) {
    throw new Error('Driver not found in context');
  }

  const startDate = new Date();
  startDate.setDate(startDate.getDate() + 30);
  const endDate = new Date(startDate);
  endDate.setDate(startDate.getDate() + 90);

  const assignDriverData = {
    site_crane_id: assignmentId,
    driver_id: driver.id,
    start_date: startDate.toISOString().split('T')[0],
    end_date: endDate.toISOString().split('T')[0],
  };

  const response = await apiAdapter.post(
    'OWNER',
    '/assignments/driver',
    assignDriverData
  );

  const driverAssignmentId = response.data.driver_assignment_id;

  if (!driverAssignmentId) {
    throw new Error('Failed to get driverAssignmentId from response');
  }

  return { driverAssignmentId };
}
