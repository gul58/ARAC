"""Capture walkthrough screenshots and a short demo video with Playwright."""
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path("/opt/cursor/artifacts")
OUT.mkdir(parents=True, exist_ok=True)
SHOTS = OUT / "screenshots"
SHOTS.mkdir(parents=True, exist_ok=True)
BASE = "http://127.0.0.1:8765"


def login(page, username, password):
    page.goto(f"{BASE}/giris/", wait_until="networkidle")
    page.fill("#id_username", username)
    page.fill("#id_password", password)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            record_video_dir=str(OUT / "pw_video"),
            record_video_size={"width": 1280, "height": 900},
            locale="tr-TR",
        )
        page = context.new_page()

        # Login page
        page.goto(f"{BASE}/giris/", wait_until="networkidle")
        page.screenshot(path=str(SHOTS / "login_page.png"), full_page=True)

        # İhale flow
        login(page, "cagla", "cagla123")
        page.screenshot(path=str(SHOTS / "ihale_regions.png"), full_page=True)

        for slug, name in [
            ("firmalar", "ihale_companies.png"),
            ("formenler", "ihale_foremen.png"),
            ("araclar", "ihale_vehicles.png"),
            ("soforler", "ihale_drivers.png"),
        ]:
            page.goto(f"{BASE}/ihale/{slug}/", wait_until="networkidle")
            page.screenshot(path=str(SHOTS / name), full_page=True)

        # Logout
        page.locator("form[action='/cikis/'] button").click()
        page.wait_for_load_state("networkidle")

        # Formen flow
        login(page, "muhammet", "formen123")
        page.screenshot(path=str(SHOTS / "formen_home.png"), full_page=True)

        page.goto(f"{BASE}/formen/gorev-emri/yeni/", wait_until="networkidle")
        page.wait_for_timeout(500)
        page.screenshot(path=str(SHOTS / "formen_task_form.png"), full_page=True)

        # Create a task
        page.fill("#id_departure_local", "16.09.2026 08:30")
        page.fill("#id_arrival_local", "16.09.2026 16:45")
        page.fill("#id_task_type", "Yol bakım")
        page.fill("#id_destination", "Derince şantiye")
        page.click("button.btn-save-task")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(SHOTS / "formen_task_list.png"), full_page=True)

        # Edit page
        edit = page.locator("a.btn-edit").first
        if edit.count():
            edit.click()
            page.wait_for_load_state("networkidle")
            page.screenshot(path=str(SHOTS / "formen_task_edit.png"), full_page=True)

        context.close()
        browser.close()

        # Move recorded video to artifacts with a clear name
        videos = list((OUT / "pw_video").glob("*.webm"))
        if videos:
            dest = OUT / "demo_ihale_formen_gorev_emri.webm"
            videos[0].replace(dest)
            print(f"VIDEO:{dest}")
        print("SHOTS_OK")
        for f in sorted(SHOTS.glob("*.png")):
            print(f"SHOT:{f}")


if __name__ == "__main__":
    main()
