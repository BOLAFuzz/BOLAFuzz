# -*-coding:utf-8 -*-
from seleniumwire import webdriver
from seleniumwire.request import Request, Response



class BrowserRecorder:
    def __init__(self, url, output_dir):
        # initialize
        self.url = url
        self.driver = None
        self.output_dir = output_dir
        self.chromedriver_path = '/Users/alphag0/Desktop/论文/ACFuzz/crawler/bin/chromedriver'  # https://googlechromelabs.github.io/chrome-for-testing/

    def setup_driver(self):
        # create the driver with seleniumwire_options options
        options = webdriver.ChromeOptions()
        seleniumwire_options = {
            'request_storage_base_dir': self.output_dir,
            'verify_ssl': False,
            'ignore_http_methods': ["OPTIONS", "HEAD", "CONNECT", "TRACE", "PATCH"],
        }
        self.driver = webdriver.Chrome(
            options=options,
            seleniumwire_options=seleniumwire_options,
        )

    def clear_driver(self):
        # clear the driver
        if self.driver:
            self.driver.quit()

    def run_driver(self):
        if not self.driver:
            self.setup_driver()
        self.driver.get(self.url)

    def print_visited_urls(self):
        """
        打印人为操作过程中访问过的目标URL。
        """
        if self.driver:
            while True:
                for request in self.driver.requests:
                    if request.response:
                            print(request.url)


if __name__ == "__main__":
    url = "http://www.ciscn.cn/"
    output_dir = "/Users/alphag0/Desktop/论文/ACFuzz/crawler/output"
    recorder = BrowserRecorder(url=url, output_dir=output_dir)
    
    try:
        recorder.run_driver()
        recorder.print_visited_urls()
    finally:
        recorder.clear_driver()
