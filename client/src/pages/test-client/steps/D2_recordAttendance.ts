import { apiAdapter } from '../transport/apiAdapter';
import { StepInput, runStep } from './types';

type RecordAttendanceInput = StepInput & {
  driverAssignmentId: string;
};

export async function recordAttendance(input: RecordAttendanceInput): Promise<{}> {
  return runStep('D2.recordAttendance', async () => {
    const { driverAssignmentId } = input;
    if (!driverAssignmentId) throw new Error('driverAssignmentId is required');

    const workDate = new Date();
    workDate.setDate(workDate.getDate() + 30);
    const workDateStr = workDate.toISOString().split('T')[0];

    const attendanceData = {
        driver_assignment_id: driverAssignmentId,
        work_date: workDateStr,
        check_in_at: `${workDateStr}T08:00:00Z`,
        check_out_at: `${workDateStr}T17:00:00Z`,
    };

    await apiAdapter.post('DRIVER', '/assignments/attendance', attendanceData);

    return {};
  });
}
