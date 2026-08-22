"""
Live portal scraper with automatic CAPTCHA‑selector fallback.

If the configured selector does not locate a CAPTCHA image, the script now:
  1. Saves the full HTML of the login page to `login_page_dump.html`.
  2. Prints a clear message telling you to open that file, locate the CAPTCHA `<img>` tag, and update `portal/config.json`.
  3. Exits gracefully so you can fix the selector and re‑run.

The selector is stored in `portal/config.json` (default: `img[src*='Captcha']`).
"""

import json, os, subprocess, sys

# Ensure UTF‑8 console output on Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add repository root to PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portal.webcmd_adapter import WebCMDAdapter, _load_env_file

_load_env_file()

# ---------------------------------------------------------------------
# Helper to load the CAPTCHA selector from config.json (git‑ignored).
# ---------------------------------------------------------------------
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
DEFAULT_SELECTOR = "img[src*='Captcha']"  # works for the current page

def load_captcha_selector() -> str:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                selector = cfg.get("captcha_selector", DEFAULT_SELECTOR)
                return selector or DEFAULT_SELECTOR
        except Exception as e:
            print(f"[⚠️] Failed to read config.json ({e}); using default selector.")
    return DEFAULT_SELECTOR

CAPTCHA_SELECTOR = load_captcha_selector()

def solve_captcha_with_node(base64_data: str) -> str:
    """Run the Node OCR helper (`ocr_solver.js`) on a base64 PNG and return the text."""
    solver_script = os.path.join(os.path.dirname(__file__), "adapters", "ocr_solver.js")
    try:
        result = subprocess.run(
            ["node", solver_script, base64_data],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            payload = json.loads(result.stdout.strip())
            return payload.get("captchaText", "").strip()
    except Exception as exc:
        print(f"[OCR] Failure: {exc}")
    return ""

def dump_page_html(html: str, filename: str = "login_page_dump.html"):
    """Write the raw HTML to a file for manual inspection."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[⚠️] Full login page saved to \"{filename}\" – open it and locate the <img> tag that displays the CAPTCHA.\n    Then update `portal/config.json` with a selector that matches that element, e.g.\n    {{\n        \"captcha_selector\": \"#myCaptchaImg\"\n    }}\n    After saving the config, re‑run the scraper.")
    except Exception as e:
        print(f"[⚠️] Could not write HTML dump: {e}")

def main():
    username = os.getenv("KP_USERNAME", "2560403")
    password = os.getenv("KP_PASSWORD", "53249901")
    base_url = os.getenv("KP_BASE_URL", "https://kp.christuniversity.in/KnowledgePro")

    print("=" * 60)
    print(f"LIVE PORTAL DEMO – Student {username}")
    print(f"Target: {base_url}")
    print(f"Using CAPTCHA selector: {CAPTCHA_SELECTOR}")
    print("=" * 60)

    adapter = WebCMDAdapter()
    bin_path = adapter._get_webcmd_bin()
    session_id = adapter._ensure_session()

    # ---------------------------------------------------------------
    # STEP 1 – Load login page, fill credentials, try to locate CAPTCHA
    # ---------------------------------------------------------------
    print("\n[1] Opening login page & waiting for CAPTCHA image…")
    step1_js = f"""
    await page.goto('{base_url}/StudentLogin.do', {{ waitUntil: 'networkidle', timeout: 30000 }});
    await page.fill('#username', '{username}');
    await page.fill('#password', '{password}');
    // Wait up to 15 s for the selector defined in Python.
    const captchaImg = await page.waitForSelector('{CAPTCHA_SELECTOR}', {{ timeout: 15000 }}).catch(() => null);
    let dataUrl = null;
    if (captchaImg) {{
        dataUrl = await page.evaluate(img => {{
            const canvas = document.createElement('canvas');
            canvas.width = img.naturalWidth || img.width;
            canvas.height = img.naturalHeight || img.height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            return canvas.toDataURL('image/png');
        }}, captchaImg);
    }}
    // Also output the whole page HTML for fallback diagnostics.
    const fullHtml = await page.content();
    console.log(JSON.stringify({{ captchaData: dataUrl, html: fullHtml }}));
    """
    step1_path = os.path.join(os.path.dirname(__file__), "adapters", "_temp_step1.js")
    with open(step1_path, "w", encoding="utf-8") as f:
        f.write(step1_js)

    cmd1 = [bin_path, "--profile", adapter.profile]
    if session_id:
        cmd1.extend(["--session", session_id])
    cmd1.extend(["browser", "run", "--file", step1_path])
    res1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=45, shell=(sys.platform == "win32"))

    # Extract the JSON payload from the console output.
    payload = None
    for line in (res1.stdout + "\n" + res1.stderr).splitlines():
        if "captchaData" in line:
            try:
                start = line.find('{')
                end = line.rfind('}')
                if start != -1 and end != -1:
                    payload = json.loads(line[start:end+1])
                    break
            except Exception:
                continue
    if payload is None:
        print("[⚠️] Unexpected output – cannot parse page data. aborting.")
        return

    captcha_data_url = payload.get('captchaData')
    if not captcha_data_url:
        # No CAPTCHA image found – dump full HTML for manual inspection.
        dump_page_html(payload.get('html', ''), filename="login_page_dump.html")
        print("[❌] CAPTCHA element not found – script stopped. Update `portal/config.json` with a correct selector and retry.")
        return
    else:
        print("  [✅] CAPTCHA image captured – sending to OCR…")
        solved = solve_captcha_with_node(captcha_data_url)
        print(f"  [🧩] OCR result: '{solved}'")

    # ---------------------------------------------------------------
    # STEP 2 – Fill OCR result (if any) into possible fields & submit.
    # ---------------------------------------------------------------
    print("\n[2] Submitting login form…")
    step2_js = f"""
    if ('{solved}') {{
        await page.fill('input[name="enteredCaptcha"]', '{solved}');
        const alt = await page.$('#captchaBox');
        if (alt) await alt.fill('{solved}');
    }}
    await Promise.all([
        page.waitForNavigation({{ waitUntil: 'networkidle', timeout: 20000 }}).catch(() => {{}}),
        page.click('button[type="submit"], input[type="submit"], button:has-text("Login")')
    ]);
    const afterUrl = await page.url();
    console.log(JSON.stringify({{ afterUrl }}));
    """
    step2_path = os.path.join(os.path.dirname(__file__), "adapters", "_temp_step2.js")
    with open(step2_path, "w", encoding="utf-8") as f:
        f.write(step2_js)
    cmd2 = [bin_path, "--profile", adapter.profile]
    if session_id:
        cmd2.extend(["--session", session_id])
    cmd2.extend(["browser", "run", "--file", step2_path])
    subprocess.run(cmd2, capture_output=True, text=True, timeout=45, shell=(sys.platform == "win32"))
    print("  [🔎] Login submission finished.")

    # ---------------------------------------------------------------
    # STEP 3 – Fetch attendance summary.
    # ---------------------------------------------------------------
    print("\n[3] Pulling Attendance Summary…")
    step3_js = f"""
    await page.goto('{base_url}/StudentLogin.do?method=initStudentWiseAttendanceSummary', {{ waitUntil: 'networkidle', timeout: 30000 }});
    const summary = await page.evaluate(() => {{
        const txt = document.body.innerText || '';
        const rows = Array.from(document.querySelectorAll('table tr'));
        const attend = [];
        for (const r of rows) {{
            const cells = Array.from(r.querySelectorAll('td, th')).map(c => c.innerText.trim());
            if (cells.length >= 4) {{
                const held = parseInt(cells[2].replace(/[^\\d]/g, ''), 10);
                const att = parseInt(cells[3].replace(/[^\\d]/g, ''), 10);
                if (!isNaN(held) && !isNaN(att)) {{
                    attend.push({{
                        code: cells[0],
                        name: cells[1],
                        held: held,
                        attended: att,
                        pct: cells[4] || ''
                    }});
                }}
            }}
        }}
        return {{ title: document.title, attendance: attend, snippet: txt.substring(0, 300) }};
    }});
    // Logout to avoid the 15‑minute session lockout.
    try {{
        await page.goto('{base_url}/StudentLogin.do?method=logout', {{ timeout: 5000 }}).catch(() => {{}});
    }} catch(e) {{}}
    console.log(JSON.stringify(summary));
    """
    step3_path = os.path.join(os.path.dirname(__file__), "adapters", "_temp_step3.js")
    with open(step3_path, "w", encoding="utf-8") as f:
        f.write(step3_js)
    cmd3 = [bin_path, "--profile", adapter.profile]
    if session_id:
        cmd3.extend(["--session", session_id])
    cmd3.extend(["browser", "run", "--file", step3_path])
    res3 = subprocess.run(cmd3, capture_output=True, text=True, timeout=45, shell=(sys.platform == "win32"))

    print("\n" + "=" * 60)
    print("LIVE SCRAPER RESULT")
    print("=" * 60)
    print(res3.stdout)

if __name__ == "__main__":
    main()
