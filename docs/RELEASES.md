# Release Notes

## Version 0.4.0 (DEV Authentication & Test Client Refactor)

This release introduces a complete, database-backed, development-mode authentication system and refactors the test client to simulate a realistic multi-user workflow.

### ✨ New Features

-   **DEV Authentication System**:
    -   Implemented a full set of authentication endpoints: `/api/v1/auth/login`, `/refresh`, and `/logout`.
    -   The `/login` endpoint now authenticates users against the `ops.users` table in the database.
    -   Added user profile endpoints: `/api/v1/me`, `/me/permissions`, and `/me/bootstrap`.
    -   Introduced a flexible `get_current_user` dependency that reads a `dev` token from the `Authorization` header.
    -   Added a `require_roles` decorator for simple, role-based access control (RBAC) on protected endpoints.
-   **Multi-User Test Client**:
    -   Refactored the test client to support a multi-user workflow.
    -   The single "Login" step was replaced by three distinct, role-based login steps:
        -   **A1: Safety Manager Login**
        -   **A2: Manufacturer Login**
        -   **A3: Driver Login**
    -   The test client now uses real credentials from the database seeder to perform logins.
    -   Subsequent workflow steps (B1, B2, etc.) now use the correct token for the actor performing the action.
-   **Improved Project Structure**:
    -   All documentation files (`.md`) were moved into a dedicated `docs/` folder to clean up the root directory.

### 🐞 Bug Fixes

-   **Resolved `422 Unprocessable Content` on Login**: Fixed a validation error caused by test user emails with a non-standard `.local` domain. The database seeder and test client were updated to use the standards-compliant `@example.com` domain.
-   **Fixed Broken Unit Tests**: Repaired outdated unit tests in `tests/unit/test_routers.py` to align with the application's current routing structure.
-   **Added Missing Dependency**: Added `pydantic[email]` to `requirements.txt` to support strict email validation.

### 🛠️ Developer Experience

-   Added extensive request logging middleware to aid in debugging.
-   Updated `openapi.yaml` to `v0.4.0` and added complete definitions for all new authentication and user endpoints.

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
