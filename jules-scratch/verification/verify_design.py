from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:5173")

        # Wait for the page to load and the button to be ready
        page.wait_for_selector('button:has-text("Initiate Full Workflow")')

        # Click the button to start the workflow
        page.click('button:has-text("Initiate Full Workflow")')

        # Wait for a few steps to complete to show progress
        page.wait_for_timeout(5000) # 5 seconds

        page.screenshot(path="jules-scratch/verification/design_verification.png")
        browser.close()

if __name__ == "__main__":
    run()
