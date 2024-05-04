import json
import time
from io import BytesIO
from typing import List

from PIL import Image
from playwright.sync_api import sync_playwright

vimium_path = "./vimium"


class Vimbot:
    console_logs: List[str]
    def __init__(self, headless=False):
        self.console_logs = []
        self.context = (
            sync_playwright()
            .start()
            .chromium.launch_persistent_context(
                "",
                headless=headless,
                args=[
                    f"--disable-extensions-except={vimium_path}",
                    f"--load-extension={vimium_path}",
                    #f"--auto-open-devtools-for-tabs",
                    "--disable-http2",
                ],
                geolocation={"latitude":35.6769, "longitude":139.65400},
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0"
                },
                ignore_https_errors=True,
            )
        )
        self.page = self.context.new_page()
        self.page.set_viewport_size({"width": 1080, "height": 1080})
        self.page.on("console", lambda msg: self.process_console_log(msg))
        self.context.add_cookies([
            {
                "name": "cookie_name",
                "value": "cookie_value",
                "url": "https://example.com"
            }
        ])
        self.context.set_offline(False)  # Ensure online mode

    def process_console_log(self, msg):
        log_text = msg.text.strip()
        if "python event bridge" in log_text:
            # Extract the JSON string by removing the substring
            json_string = log_text.replace("python event bridge ", "").strip()
            try:
                # Parse the JSON string into an object
                hint_descriptors = json.loads(json_string)
                # Save the object to a local variable
                self.local_hint_descriptors = hint_descriptors
                print("Hint Markers saved to local variable.")
            except json.JSONDecodeError:
                print("Invalid JSON string in console log.")
        else:
            # Append the console log as is
            self.console_logs.append(log_text)

    def get_console_logs(self):
        return self.console_logs

    def perform_action(self, action):
        if "done" in action:
            return True
        if "click" in action and "type" in action:
            self.click(action["click"])
            self.type(action["type"])
        if "navigate" in action:
            self.navigate(action["navigate"])
        if "scroll_up" in action:
            self.scroll_up()
        if "scroll_down" in action:
            self.scroll_down()
        elif "type" in action:
            self.type(action["type"])
        elif "click" in action:
            self.click(action["click"])

    def navigate(self, url):
        self.page.goto(url=url if "://" in url else "https://" + url, timeout=60000)

    def type(self, text):
        time.sleep(1)
        self.page.keyboard.type(text)
        self.page.keyboard.press("Enter")

    def click(self, text):
        self.page.keyboard.type(text)

    def scroll_up(self):
        self.page.keyboard.down('k')
        self.page.wait_for_timeout(1500)
        self.page.keyboard.up('k')

    def scroll_down(self):
        self.page.keyboard.down('j')
        self.page.wait_for_timeout(1500)
        self.page.keyboard.up('j')

    def capture(self):
        # capture a screenshot with vim bindings on the screen
        self.page.keyboard.press("Escape")
        self.page.keyboard.type("f")

        screenshot = Image.open(BytesIO(self.page.screenshot())).convert("RGB")
        return screenshot
