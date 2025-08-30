from playwright.sync_api import sync_playwright, expect

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Listen for console messages
            page.on("console", lambda msg: print(f"BROWSER LOG: {msg.text}"))

            # 1. Navigate to the page
            page.goto("http://localhost:3000/test-client", timeout=10000)

            # 2. Find and click the button
            run_button = page.get_by_role("button", name="Run Full Workflow")
            expect(run_button).to_be_visible()
            run_button.click()

            # 3. Assert that the workflow has started and the first step succeeded
            running_button = page.get_by_role("button", name="Executing...")
            expect(running_button).to_be_visible()

            # Assert that the first step was successful
            expect(page.get_by_text("Step successful: B1.createSite")).to_be_visible(timeout=10000)

            # 4. Take a screenshot
            page.screenshot(path="jules-scratch/verification/verification.png")

        except Exception as e:
            print(f"An error occurred: {e}")
            # Take a screenshot even on failure for debugging
            page.screenshot(path="jules-scratch/verification/error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
