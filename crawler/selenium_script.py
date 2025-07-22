# -*- coding: utf-8 -*-
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class SeleniumHandler:
    def __init__(self, url: str, proxy: str, chrome_driver_path: str):
        self.url = url
        self.driver = None
        self.proxy = proxy
        self.chrome_driver_path = chrome_driver_path

    def setup_driver(self) -> None:
        """Set up the Chrome webdriver with the given proxy settings."""
        service = Service(executable_path=self.chrome_driver_path)
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--allow-insecure-localhost')
        chrome_options.add_argument(f'--proxy-server={self.proxy}')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def run_selenium(self) -> None:
        """Run the Selenium webdriver to visit the specified URL."""
        if self.driver is None:
            self.setup_driver()
        self.driver.get(self.url)
        input("[>] Press Enter to exit...")
        self.driver.quit()


def run_mitmdump() -> None:
    """Start mitmdump with the specified script and port."""
    print('[>] Starting the terminal...')
    apple_script = """
    tell application "Terminal"
        activate
        delay 1
        do script "mitmdump -s mitm_script.py -p 38080"
    end tell
    """
    subprocess.call(f"osascript -e '{apple_script}'", shell=True)


def close_terminal() -> None:
    """Close the Terminal application."""
    print('[>] Closing the terminal...')
    apple_script = """
    tell application "Terminal"
        close (every window)
    end tell
    """
    subprocess.call(f"osascript -e '{apple_script}'", shell=True)


def main() -> None:
    """Main function to start mitmdump, run Selenium, and close the terminal."""
    # run_mitmdump()
    # time.sleep(1)

    url = "about:blank"
    proxy_server = "127.0.0.1:38080"
    chrome_driver_path = "/usr/local/bin/chromedriver"
    selenium_handler = SeleniumHandler(url=url, proxy=proxy_server, chrome_driver_path=chrome_driver_path)
    selenium_handler.run_selenium()

    # close_terminal()


if __name__ == "__main__":
    main()
