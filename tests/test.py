# -*-coding:utf-8 -*-
import tldextract
from urllib.parse import urlparse, parse_qs
from DrissionPage import ChromiumPage, ChromiumOptions, Chromium


class BrowserSimulator:
    def __init__(self, url):
        """初始化参数"""
        self.url = url
        self.domain = tldextract.extract(self.url).domain
        self.co = ChromiumOptions().set_argument('--start-maximized').no_imgs(True).no_js(True).mute(True)
        # self.page = ChromiumPage(self.co)
        self.data_packet = []
        self.browser = Chromium(self.co)
        self.page = self.browser.latest_tab
    

    def open_url(self):
        """打开指定的URL"""
        self.page.get(self.url)
        print("[+] browser opened...")


    def record_request_response(self):
        """记录请求和响应"""
        while True:
            self.page.listen.start(self.domain)
            input()
            try:
                # 等待一个数据包, 超时时间为5秒
                packet = self.page.listen.wait(count=1, fit_count=False, timeout=15)
                print(packet)
                # 过滤掉不需要记录的文件类型
                if (packet.url.endswith('.js') or 
                    packet.url.endswith('.css') or 
                    packet.url.endswith('.ico') or 
                    packet.url.endswith('.png') or 
                    packet.url.endswith('.jpg') or 
                    packet.url.endswith('.jpeg') or 
                    packet.url.endswith('.gif') or 
                    packet.url.endswith('.txt') or 
                    packet.url.endswith('.json')):
                    continue
                # 检查URL是否属于目标域名
                if tldextract.extract(packet.url).domain != self.domain:
                    continue
                # 记录数据包
                self.data_packet.append(packet)
                print(packet.request)
                print(packet.response)

            except RuntimeError as e:
                print(f"error: {e}")
                break

            # 停止监听器, 等待下一次请求
            self.page.listen.stop()



        # for packet in self.page.listen.wait(count=99999999, fit_count=False, timeout=None):
        #     if packet.url.endswith('.js') or packet.url.endswith('.css') or packet.url.endswith(
        #             '.ico') or packet.url.endswith('.png') or packet.url.endswith('.jpg') or packet.url.endswith('.jpeg') or packet.url.endswith('.gif') or packet.url.endswith('.txt') or packet.url.endswith('.json'):
        #         continue
        #     if tldextract.extract(packet.url).domain != self.domain:
        #         continue
        #     self.data_packet.append(packet)
        #     print(self.data_packet)

    def start_browser_and_listen(self):
        """打开浏览器，导航到URL，并开始监听网络请求"""
        try:
            # 打开浏览器并导航到指定的URL
            self.page.get(self.url)
            print(f"导航到 {self.url} 成功")
            
            # 启动网络请求监听器
            self.page.listen.start()
            print("开始监听网络请求...")
            
            # 让用户自由操作浏览器
            print("请在浏览器中自由操作，程序将记录所有请求和响应...")
            
            # 记录网络请求和响应
            self.record_packets()
            
        except Exception as e:
            print(f"发生错误：{e}")
        finally:
            # 停止监听
            self.page.listen.stop()
            print("停止监听网络请求。")
            # 关闭浏览器
            self.close_browser()
            print("浏览器已关闭。")


    def record_packets(self):
        """记录网络请求和响应"""
        print(1)
        try:
            # 使用一个循环来监听网络请求
            for packet in self.page.listen.steps(timeout=10):  # 设置超时时间，防止无限循环
                print(2)
                # 记录请求和响应信息
                self.log_packet(packet)
                
        except Exception as e:
            print(f"记录请求和响应时发生错误：{e}")


    def log_packet(self, packet):
        """打印单个数据包的详细信息"""
        print("-" * 40)
        print(f"请求URL: {packet.url}")
        self.url_parse(packet.url)
        print(f"请求方法: {packet.method}")
        print(f"请求头: {packet.request.headers}")
        print(f"响应状态码: {packet.response.status}")
        print(f"响应头: {packet.response.headers}")
        if packet.response.body:
            print(f"响应体: {packet.response.body}")
        print("-" * 40)


    def url_parse(self, url):
        """解析URL"""
        parsed_url = urlparse(url)
        url_domain = parsed_url.netloc
        url_path = parsed_url.path
        url_query_params = parse_qs(parsed_url.query)
        print(f"url_domain：{url_domain}")
        print(f"url_path：{url_path}")
        print(f"url_query_params：{url_query_params}")


    def close_browser(self):
        """关闭浏览器"""
        self.browser.driver.quit()
        print("[+] browser closed...")


if __name__ == "__main__":
    url = "https://www.baidu.com/"
    simulator = BrowserSimulator(url=url)
    try:
        simulator.start_browser_and_listen()
        # simulator.record_request_response()
    finally:
        simulator.close_browser()