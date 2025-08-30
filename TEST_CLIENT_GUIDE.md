# Developer Guide: The Interactive Test Client

## 1. Overview

The `/test-client` page is an interactive, visual tool designed to serve as a "living document" for the core business workflow of the DY Crane Safety Management system. Its primary purpose is to help developers understand, test, and debug the end-to-end sequence of operations, from user authentication to final artifact generation.

This guide is intended for both **backend** and **frontend** developers.
-   **Backend Developers** can use it to trigger specific API calls in sequence and observe the system's state changes.
-   **Frontend Developers** can use it as a reference for how to interact with the API and manage application state for various user roles.

## 2. How to Use the UI

The test client UI is composed of three main panels:

![Test Client UI Layout](https://i.imgur.com/your-image-here.png) <!-- Placeholder for a future screenshot -->

### a. Workflow Rail (Left Panel)

This panel lists all the steps in the business workflow, from A1 to F2.
-   **Status Icon**: Indicates the current state of each step (● idle, ► in-progress, ✓ done, ✗ error).
-   **Run Step Button**: Executes a single, specific workflow step. This is useful for testing a particular part of the flow in isolation.
-   **Auto Run All Button**: Executes the entire workflow from beginning to end. This is the primary way to test the full end-to-end sequence.

### b. Step Panel (Center Panel)

This panel shows the details of the currently selected workflow step.
-   **Description Tab**: Explains the purpose of the step in the context of the business logic.
-   **Data Flow Tab**: Shows what data the step requires from the application context (`In`) and what data it produces and adds back to the context (`Out`). This is crucial for understanding how data is passed between steps.
-   **Notes Tab**: A scratchpad for developers to leave temporary notes or observations during a test run.

### c. Log Console (Right Panel)

This panel displays a real-time, timestamped log of events as they occur.
-   **Client Events**: Shows actions happening in the UI and state changes.
-   **API Events**: Logs every API request and response, making it easy to see what's being sent to and received from the server.
-   **System Events**: Indicates the start, end, or failure of steps and workflows.

### d. Reset Workflow Data Button (Top Right)

This is a critical button for repeatable testing.
-   **Function**: It calls the `POST /api/health/reset-transactional` endpoint on the server.
-   **Action**: It clears all **transactional data** (sites, assignments, documents, etc.) from the database, while preserving **master data** (users, cranes, orgs).
-   **When to Use**: Press this button before starting a new `Auto Run All` to ensure the test runs in a clean environment and avoid `409 Conflict` errors from previously assigned resources.

## 3. The Business Workflow (A1 - F2)

This section details each step of the main business workflow as represented in the test client.

---

### Phase A — Auth & Env

#### **[A1] 역할별 로그인/세션 준비 (Prepare Sessions by Role)**
-   **Actor**: SM, MFR, OWN, DRV (Safety Manager, Manufacturer, Owner, Driver)
-   **Description**: Prepares the authentication sessions for all user roles that will be used in the scenario. It secures role-based tokens and minimal user profiles, allowing subsequent steps to reference them via a shared context.
-   **Data Flow**:
    -   **Out**: `tokens.*`, `users.*`

#### **[A2] 환경/스키마 확인 (Check Environment/Schema)**
-   **Actor**: SYSTEM
-   **Description**: Performs a preliminary check on service availability and the existence of necessary database schemas, views, and indexes. Any missing items are recorded as a checklist for server/DB enhancement work (no immediate modifications are made).
-   **Data Flow**:
    -   **Out**: `env.checklist`

---

### Phase B — Site Request/Approval

#### **[B1] 현장 생성 요청 (Request Site Creation)**
-   **Actor**: SM
-   **Description**: Submits a "request" for a new construction site, following a request-based model rather than direct creation.
-   **Data Flow**:
    -   **In**: `users.SAFETY_MANAGER`
    -   **Out**: `site.siteId`, `site.requestId`

#### **[B2] 현장 요청 승인 (Approve Site Request)**
-   **Actor**: MFR
-   **Description**: Approves a pending site creation request. It's assumed that the state transition for the request and the site is handled atomically on the server; only the result is reflected in the context.
-   **Data Flow**:
    -   **In**: `site.siteId`, `users.MANUFACTURER`
    -   **Out**: `site.status`

#### **[B3] 내 현장 확인 (Verify My Sites)**
-   **Actor**: SM
-   **Description**: Confirms that the newly approved site is now reflected in the user's list of sites. This serves as a baseline for subsequent assignment and documentation steps.
-   **Data Flow**:
    -   **In**: `users.SAFETY_MANAGER`
    -   **Out**: `site.list`

---

### Phase C — Owner/Crane & Deploy Request

#### **[C1] 사업주 목록(통계) (List Owners with Stats)**
-   **Actor**: SM
-   **Description**: Retrieves a list of owner "cards" along with the count of their available and total cranes. This is the starting point for selecting a crane for assignment.
-   **Data Flow**:
    -   **Out**: `owners[]`

#### **[C2] 사업주별 크레인(가용 필터) (List Cranes by Owner - Available Filter)**
-   **Actor**: SM
-   **Description**: Fetches the list of available cranes for a selected owner, securing the necessary identifiers for the subsequent deployment request.
-   **Data Flow**:
    -   **In**: `owners[0].id`
    -   **Out**: `cranes.byOwner[ownerId].available[]`

#### **[C3] 크레인 현장 배치 ‘요청’ 생성 (Create Crane Deployment 'Request')**
-   **Actor**: SM
-   **Description**: Selects an available crane and requests its deployment to a specific site, following the request/approval model.
-   **Data Flow**:
    -   **In**: `site.siteId`, `cranes.byOwner[ownerId].available[0].id`, `users.SAFETY_MANAGER`
    -   **Out**: `deploy.requestId`

#### **[C4] 사업주의 요청함 확인 (Owner Checks Pending Requests)**
-   **Actor**: OWN
-   **Description**: Checks the list of incoming crane deployment requests for the owner.
-   **Data Flow**:
    -   **In**: `users.OWNER`
    -   **Out**: `owner.pendingRequests[]`

#### **[C5] 배치 요청 승인/거절 (Approve/Reject Deployment Request)**
-   **Actor**: OWN
-   **Description**: Approves or rejects the request. It's assumed that approval triggers a state transition for the crane and site.
-   **Data Flow**:
    -   **In**: `owner.pendingRequests[0].id`, `users.OWNER`
    -   **Out**: `deploy.status`, `crane.assigned`, `site.status`

#### **[C6] 배치 결과 검증(현장 기준) (Verify Deployment from Site Perspective)**
-   **Actor**: SM
-   -   **Description**: Confirms that the crane has been successfully assigned to the target site. This is a prerequisite for the driver scenarios.
-   **Data Flow**:
    -   **In**: `site.siteId`
    -   **Out**: `site.assignedCranes[]`

---

### Phase D — Driver Assignment & Attendance

#### **[D1] 운전자 배정 확인 (Driver Checks Assignment)**
-   **Actor**: DRV
-   **Description**: The driver queries for the crane/site they have been assigned to, confirming their eligibility to check in for work.
-   **Data Flow**:
    -   **In**: `users.DRIVER`
    -   **Out**: `driver.assigned[]`

#### **[D2] 출근 체크-인 (Check-In for Work)**
-   **Actor**: DRV
-   **Description**: Records the driver's attendance at the assigned site/crane. This is a prerequisite for subsequent documentation procedures.
-   **Data Flow**:
    -   **In**: `driver.assigned[0].id`
    -   **Out**: `attendance.latest`

---

### Phase E — Documents (Request → Submit → Review)

#### **[E1] 서류 제출 요청 (Request Document Submission)**
-   **Actor**: SM
-   **Description**: The safety manager requests a specific driver to submit documentation.
-   **Data Flow**:
    -   **In**: `site.siteId`, `users.DRIVER`, `users.SAFETY_MANAGER`
    -   **Out**: `doc.request.documentId`

#### **[E2] 운전자 서류 제출 (Driver Submits Document)**
-   **Actor**: DRV
-   **Description**: The driver submits the requested document.
-   **Data Flow**:
    -   **In**: `doc.request.documentId`, `users.DRIVER`
    -   **Out**: `doc.submitted`

#### **[E3] 서류 검토 (Review Document)**
-   **Actor**: SM
-   **Description**: The safety manager reviews and confirms the submitted document.
-   **Data Flow**:
    -   **In**: `doc.submitted.id`, `users.SAFETY_MANAGER`
    -   **Out**: `doc.reviewed`

---

### Phase F — Aggregation & Artifacts

#### **[F1] 워크플로우 집계 (Aggregate Workflow)**
-   **Actor**: SYSTEM
-   **Description**: Gathers the final state of the site, crane, request, attendance, and documents to summarize the overall success of the workflow.
-   **Data Flow**:
    -   **In**: `context`
    -   **Out**: `snapshot.final`

#### **[F2] 아티팩트 생성 (Generate Artifacts)**
-   **Actor**: SYSTEM
-   **Description**: Creates and archives final artifacts such as a JSON state snapshot, event logs, and UI screenshots.
-   **Data Flow**:
    -   **In**: `snapshot.final`
    -   **Out**: `artifacts.*` (paths/metadata)
