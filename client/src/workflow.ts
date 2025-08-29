import apiClient from './apiClient';

type Logger = (message: string) => void;

const SAFETY_MANAGER_ID = "user-safety-manager-01";
const MANUFACTURER_ID = "user-manufacturer-01";
const DRIVER_ID = "user-driver-01";
const OWNER_ORG_ID = "org-owner-01";

export async function runWorkflow(log: Logger) {
  try {
    // Step 1: Create Site
    log("STEP 1: Creating site...");
    const startDate = new Date();
    startDate.setDate(startDate.getDate() + 30);
    const endDate = new Date(startDate);
    endDate.setDate(startDate.getDate() + 90);

    const siteData = {
      name: `E2E Test Site - ${new Date().toISOString()}`,
      address: "123 Test Street, Test City",
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0],
      requested_by_id: SAFETY_MANAGER_ID,
    };
    const createSiteResponse = await apiClient.post('/sites/', siteData);
    const siteId = createSiteResponse.data.id;
    log(`  -> Site created with ID: ${siteId}`);
    log(`  -> Response: ${JSON.stringify(createSiteResponse.data, null, 2)}`);

    // Step 2: Approve Site
    log("STEP 2: Approving site...");
    const approveData = { approved_by_id: MANUFACTURER_ID };
    const approveSiteResponse = await apiClient.post(`/sites/${siteId}/approve`, approveData);
    log(`  -> Site approved.`);
    log(`  -> Response: ${JSON.stringify(approveSiteResponse.data, null, 2)}`);

    // Step 3: List Cranes
    log("STEP 3: Listing cranes...");
    const listCranesResponse = await apiClient.get(`/cranes/owners/${OWNER_ORG_ID}/cranes`);
    log(`  -> Found ${listCranesResponse.data.length} cranes.`);
    const craneId = listCranesResponse.data[0].id;
    log(`  -> Using crane with ID: ${craneId}`);
    log(`  -> Response: ${JSON.stringify(listCranesResponse.data, null, 2)}`);

    // Step 4: Assign Crane
    log("STEP 4: Assigning crane...");
    const assignCraneData = {
        site_id: siteId,
        crane_id: craneId,
        safety_manager_id: SAFETY_MANAGER_ID,
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
    };
    const assignCraneResponse = await apiClient.post('/assignments/crane', assignCraneData);
    const siteCraneId = assignCraneResponse.data.assignment_id;
    log(`  -> Crane assigned with assignment ID: ${siteCraneId}`);
    log(`  -> Response: ${JSON.stringify(assignCraneResponse.data, null, 2)}`);

    // Step 5: Assign Driver
    log("STEP 5: Assigning driver...");
    const assignDriverData = {
        site_crane_id: siteCraneId,
        driver_id: DRIVER_ID,
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
    };
    const assignDriverResponse = await apiClient.post('/assignments/driver', assignDriverData);
    const driverAssignmentId = assignDriverResponse.data.driver_assignment_id;
    log(`  -> Driver assigned with assignment ID: ${driverAssignmentId}`);
    log(`  -> Response: ${JSON.stringify(assignDriverResponse.data, null, 2)}`);

    // Step 6: Record Attendance
    log("STEP 6: Recording attendance...");
    const attendanceData = {
        driver_assignment_id: driverAssignmentId,
        work_date: startDate.toISOString().split('T')[0],
        check_in_at: `${startDate.toISOString().split('T')[0]}T08:00:00Z`,
        check_out_at: `${startDate.toISOString().split('T')[0]}T17:00:00Z`,
    };
    const attendanceResponse = await apiClient.post('/assignments/attendance', attendanceData);
    log(`  -> Attendance recorded.`);
    log(`  -> Response: ${JSON.stringify(attendanceResponse.data, null, 2)}`);

    // Step 7: Request Document
    log("STEP 7: Requesting document...");
    const docRequestData = {
        site_id: siteId,
        driver_id: DRIVER_ID,
        requested_by_id: SAFETY_MANAGER_ID,
        due_date: endDate.toISOString().split('T')[0],
    };
    const docRequestResponse = await apiClient.post('/docs/requests', docRequestData);
    const requestId = docRequestResponse.data.request_id;
    log(`  -> Document requested with request ID: ${requestId}`);
    log(`  -> Response: ${JSON.stringify(docRequestResponse.data, null, 2)}`);

    // Step 8: Submit Document
    log("STEP 8: Submitting document...");
    const docSubmitData = {
        request_id: requestId,
        doc_type: "Safety Certificate",
        file_url: "https://example.com/safety-cert.pdf"
    };
    const docSubmitResponse = await apiClient.post('/docs/items/submit', docSubmitData);
    const itemId = docSubmitResponse.data.item_id;
    log(`  -> Document submitted with item ID: ${itemId}`);
    log(`  -> Response: ${JSON.stringify(docSubmitResponse.data, null, 2)}`);

    // Step 9: Review Document
    log("STEP 9: Reviewing document...");
    const docReviewData = {
        item_id: itemId,
        reviewer_id: SAFETY_MANAGER_ID,
        approve: true
    };
    const docReviewResponse = await apiClient.post('/docs/items/review', docReviewData);
    log(`  -> Document reviewed.`);
    log(`  -> Response: ${JSON.stringify(docReviewResponse.data, null, 2)}`);


    log("\nWorkflow finished successfully!");

  } catch (error: any) {
    log(`\nERROR during workflow: ${error.message}`);
    if (error.response) {
      log(`  -> Response Data: ${JSON.stringify(error.response.data, null, 2)}`);
    }
  }
}
