import apiClient from './apiClient';

type Logger = (message: string) => void;

const SAFETY_MANAGER_ID = "user-safety-manager-01";
const MANUFACTURER_ID = "user-manufacturer-01";
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
    const listCranesResponse = await apiClient.get(`/owners/${OWNER_ORG_ID}/cranes`);
    log(`  -> Found ${listCranesResponse.data.length} cranes.`);
    log(`  -> Response: ${JSON.stringify(listCranesResponse.data, null, 2)}`);

    log("\nWorkflow finished (partially).");

  } catch (error: any) {
    log(`\nERROR during workflow: ${error.message}`);
    if (error.response) {
      log(`  -> Response Data: ${JSON.stringify(error.response.data, null, 2)}`);
    }
  }
}
