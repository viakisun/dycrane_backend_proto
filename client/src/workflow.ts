import apiClient from './apiClient';
import { Dispatch, SetStateAction } from 'react';

type Logger = (message: string, data?: any) => void;
type StatusUpdater = Dispatch<SetStateAction<Record<number, 'pending' | 'success' | 'error'>>>;


const SAFETY_MANAGER_ID = "user-safety-manager-01";
const MANUFACTURER_ID = "user-manufacturer-01";
const DRIVER_ID = "user-driver-01";
const OWNER_ORG_ID = "org-owner-01";

async function runStep<T>(step: number, title: string, log: Logger, setStatus: StatusUpdater, fn: () => Promise<T>): Promise<T | null> {
    log(`STEP ${step}: ${title}...`);
    setStatus(prev => ({ ...prev, [step]: 'pending' }));
    try {
        const result = await fn();
        log(`  -> SUCCESS: ${title}`);
        log(`  -> Response:`, result);
        setStatus(prev => ({ ...prev, [step]: 'success' }));
        return result;
    } catch (error: any) {
        log(`ERROR during step ${step}: ${error.message}`);
        if (error.response) {
            log(`  -> Response Data:`, error.response.data);
        }
        setStatus(prev => ({ ...prev, [step]: 'error' }));
        throw error; // Re-throw to stop the workflow
    }
}

export async function runWorkflow(log: Logger, setStatus: StatusUpdater) {
  try {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 30);
    const endDate = new Date(startDate);
    endDate.setDate(startDate.getDate() + 90);

    // Step 1: Create Site
    const siteData = {
      name: `E2E Test Site - ${new Date().toISOString()}`,
      address: "123 Test Street, Test City",
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0],
      requested_by_id: SAFETY_MANAGER_ID,
    };
    const createSiteResponse = await runStep(1, "Create Site", log, setStatus, () => apiClient.post('/sites/', siteData));
    const siteId = createSiteResponse?.data.id;

    // Step 2: Approve Site
    const approveData = { approved_by_id: MANUFACTURER_ID };
    await runStep(2, "Approve Site", log, setStatus, () => apiClient.post(`/sites/${siteId}/approve`, approveData));

    // Step 3: List Cranes
    const listCranesResponse = await runStep(3, "List Cranes", log, setStatus, () => apiClient.get(`/cranes/owners/${OWNER_ORG_ID}/cranes`));
    const craneId = listCranesResponse?.data[0].id;

    // Step 4: Assign Crane
    const assignCraneData = {
        site_id: siteId,
        crane_id: craneId,
        safety_manager_id: SAFETY_MANAGER_ID,
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
    };
    const assignCraneResponse = await runStep(4, "Assign Crane", log, setStatus, () => apiClient.post('/assignments/crane', assignCraneData));
    const siteCraneId = assignCraneResponse?.data.assignment_id;

    // Step 5: Assign Driver
    const assignDriverData = {
        site_crane_id: siteCraneId,
        driver_id: DRIVER_ID,
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
    };
    const assignDriverResponse = await runStep(5, "Assign Driver", log, setStatus, () => apiClient.post('/assignments/driver', assignDriverData));
    const driverAssignmentId = assignDriverResponse?.data.driver_assignment_id;

    // Step 6: Record Attendance
    const attendanceData = {
        driver_assignment_id: driverAssignmentId,
        work_date: startDate.toISOString().split('T')[0],
        check_in_at: `${startDate.toISOString().split('T')[0]}T08:00:00Z`,
        check_out_at: `${startDate.toISOString().split('T')[0]}T17:00:00Z`,
    };
    await runStep(6, "Record Attendance", log, setStatus, () => apiClient.post('/assignments/attendance', attendanceData));

    // Step 7: Request Document
    const docRequestData = {
        site_id: siteId,
        driver_id: DRIVER_ID,
        requested_by_id: SAFETY_MANAGER_ID,
        due_date: endDate.toISOString().split('T')[0],
    };
    const docRequestResponse = await runStep(7, "Request Document", log, setStatus, () => apiClient.post('/docs/requests', docRequestData));
    const requestId = docRequestResponse?.data.request_id;

    // Step 8: Submit Document
    const docSubmitData = {
        request_id: requestId,
        doc_type: "Safety Certificate",
        file_url: "https://example.com/safety-cert.pdf"
    };
    const docSubmitResponse = await runStep(8, "Submit Document", log, setStatus, () => apiClient.post('/docs/items/submit', docSubmitData));
    const itemId = docSubmitResponse?.data.item_id;

    // Step 9: Review Document
    const docReviewData = {
        item_id: itemId,
        reviewer_id: SAFETY_MANAGER_ID,
        approve: true
    };
    await runStep(9, "Review Document", log, setStatus, () => apiClient.post('/docs/items/review', docReviewData));

    log("\nWorkflow finished successfully!");

  } catch (error) {
    log(`\nWorkflow stopped due to an error.`);
  }
}
