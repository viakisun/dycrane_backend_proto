# Release Notes

## Version 0.1.0 (Initial Development)

This is the initial release of the DY Crane Safety Management developer toolkit. The primary focus of this release was to build a comprehensive, interactive test client to serve as a living developer guide for the backend API and business workflow.

### ✨ New Features

-   **Developer Guide Test Client (`/test-client`)**:
    -   Implemented a new, three-panel UI inspired by modern developer tools.
    -   **Workflow Rail**: Provides a visual representation of the entire A1-F2 business workflow, allowing for step-by-step execution or a full "Auto Run".
    -   **Step Panel**: A detailed view for each step, showing its description, the actors involved, and the flow of data in and out of the application context.
    -   **Log Console**: A real-time log of events occurring during the workflow execution.
-   **Server State Reset Functionality**:
    -   To enable robust, repeatable testing, a server-side reset mechanism was implemented.
    -   **Backend API**: A new endpoint (`POST /api/health/reset-transactional`) was added to clear all transactional data from the database while preserving master data (users, cranes, etc.).
    -   **UI Integration**: A "Reset Workflow Data" button was added to the test client, allowing users to safely reset the server state before a run.
    -   **CLI Integration**: The `dev.sh` and `db_cli.py` scripts were enhanced to support both transactional and full database resets from the command line.

### 🐞 Bug Fixes

This release includes the resolution of a complex series of interconnected bugs that were discovered during development:

-   **Resolved Blank Page on Load**: Fixed a `ReferenceError` caused by a circular dependency between the `workflowStore` and `apiAdapter`, which prevented the application from rendering.
-   **Resolved `404 Not Found` on User Fetch**: Corrected an incorrect API call that was trying to fetch users from a non-existent endpoint. The client now uses a hardcoded set of test users, aligning with the E2E test methodology.
-   **Resolved `409 Conflict` on Re-run**: This was the root cause of many issues. It was resolved by implementing the server state reset feature, preventing conflicts when re-running the workflow with resources that were assigned in a previous run.
-   **Resolved `422 Unprocessable Content` on Driver Assignment**: Fixed a bug where a necessary approval step was missing from the client-side workflow logic. The approval step was later found to be an incorrect assumption, and the real fix was the state reset.
-   **Resolved `400 Bad Request` on Document Submission**: Solved a subtle but critical bug where the database driver could not handle Pydantic's `AnyHttpUrl` type. The fix involved ensuring the data passed to the database layer was a plain string, which required a deep understanding of the Pydantic model lifecycle.

### 🛠️ Developer Experience

-   The entire test client is now data-driven via `workflow-def.ts`, making it easy to update or add new steps.
-   The state is managed centrally in `workflowStore.ts` using Zustand.
-   The styling follows a consistent, developer-friendly dark theme.
