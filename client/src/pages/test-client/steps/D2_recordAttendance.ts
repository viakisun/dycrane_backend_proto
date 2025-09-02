import { apiAdapter } from '../transport/apiAdapter';
import { StepInput } from './types';

type RecordAttendanceInput = StepInput & {
  driverAssignmentId: string;
};

export async function recordAttendance(input: RecordAttendanceInput): Promise<void> {
  const { driverAssignmentId } = input;
  const workDate = new Date();
  workDate.setDate(workDate.getDate() + 30);

  const attendanceData = {
    driver_assignment_id: driverAssignmentId,
    work_date: workDate.toISOString().split('T')[0],
    check_in_at: `${workDate.toISOString().split('T')[0]}T08:00:00Z`,
    check_out_at: `${workDate.toISOString().split('T')[0]}T17:00:00Z`,
  };

  await apiAdapter.post('DRIVER', '/attendances', attendanceData);
}
