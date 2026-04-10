from playwright.sync_api import sync_playwright

def get_total_banco():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            context = browser.new_context(storage_state="estado.json")
            page = context.new_page()

            page.goto("https://portalpersonas.bancochile.cl")

            # validar sesión
            if "login" in page.url:
                print("Sesión expirada")
                browser.close()
                return 0

            page.wait_for_timeout(5000)

            elementos = page.locator("text=$").all_text_contents()

            total = 0

            for e in elementos:
                try:
                    limpio = e.replace("$", "").replace(".", "").replace(",", "")
                    monto = int(limpio)
                    total += monto
                except:
                    continue

            browser.close()
            return total

    except Exception as e:
        print("ERROR PLAYWRIGHT:", e)
        return 0