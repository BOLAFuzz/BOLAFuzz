# -*-coding:utf-8 -*-
import json
import asyncio
from DrissionPage import ChromiumPage, ChromiumOptions, WebPage
from init import init
import yaml
import tldextract


class BrowserSimulator:
    def __init__(self):
        self.captured_data = []
        self.domain = None
        self.options = None
        self.browser = None  # 添加一个属性来存储浏览器实例

    def open_browser(self, url):
        """打开一个新的浏览器实例"""
        self.domain = tldextract.extract(url).domain
        self.options = ChromiumOptions().set_argument('--start-maximized')
        self.browser = WebPage.open(mode='d', chromium_options=self.options)
        print("[+] Browser opened...")


    def close_browser(self):
        """关闭当前浏览器实例"""
        if self.browser:
            self.browser.quit()
            self.browser = None
            print("[+] Browser closed...")

    def is_browser_closed(self):
        """检查浏览器是否已关闭"""
        if self.browser:
            try:
                return False
            except Exception:
                return True
        return True

    def run(self, websites):
        """循环访问网站配置文件"""

        for website in websites:
            self.open_browser(website['url'])
            self.save_captured_data(f"{website['name']}_captured_data.json")

        for website in websites:
            self.open_browser()
            print(f"正在访问网站: {site['url']}")
            # 在这里进行人工操作
            # ...

            # 等待人工操作完成
            while not self.is_browser_closed():
                asyncio.sleep(1)

            self.close_browser()
            print(f"已完成网站: {site['url']} 的操作")


def load_website_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as file:
        websites = yaml.safe_load(file)
    return websites

if __name__ == '__main__':
    # 使用示例
    website_config = load_website_config('config/websites.yaml')
    simulator = BrowserSimulator()
    simulator.process_websites




