from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://portalpersonas.bancochile.cl")

    input("👉 Inicia sesión manual y presiona ENTER...")

    context.storage_state(path="estado.json")
    browser.close()