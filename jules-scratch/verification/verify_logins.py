from playwright.sync_api import sync_playwright, expect

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to the test client page
            page.goto("http://localhost:3000/test-client", timeout=30000)

            # Find the step cards by their title
            sm_login_card = page.locator('div.p-6:has-text("A1: 안전관리자 로그인")')
            mfr_login_card = page.locator('div.p-6:has-text("A2: 제조사 로그인")')
            driver_login_card = page.locator('div.p-6:has-text("A3: 운전자 로그인")')

            # --- Step A1: Safety Manager Login ---
            sm_run_button = sm_login_card.get_by_role("button", name="Run")
            expect(sm_run_button).to_be_enabled()
            sm_run_button.click()
            # Wait for the status indicator to turn green (done)
            expect(sm_login_card.locator('div[data-status="done"]')).to_be_visible(timeout=15000)

            # --- Step A2: Manufacturer Login ---
            mfr_run_button = mfr_login_card.get_by_role("button", name="Run")
            expect(mfr_run_button).to_be_enabled()
            mfr_run_button.click()
            expect(mfr_login_card.locator('div[data-status="done"]')).to_be_visible(timeout=15000)

            # --- Step A3: Driver Login ---
            driver_run_button = driver_login_card.get_by_role("button", name="Run")
            expect(driver_run_button).to_be_enabled()
            driver_run_button.click()
            expect(driver_login_card.locator('div[data-status="done"]')).to_be_visible(timeout=15000)

            # Take a screenshot of the completed login steps
            page.screenshot(path="jules-scratch/verification/verification.png")
            print("Screenshot taken successfully.")

        except Exception as e:
            print(f"An error occurred: {e}")
            page.screenshot(path="jules-scratch/verification/error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
