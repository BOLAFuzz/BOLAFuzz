import random
import string
import time

from DrissionPage import WebPage
from DrissionPage import ChromiumOptions, ChromiumPage
import tldextract


class AutoLogin:
    def __init__(self, url, username, password, input_text):
        self.co = ChromiumOptions().set_argument('--start-maximized').new_env()
        self.target_url = url
        self.old_url = ''
        self.domain = tldextract.extract(self.target_url).domain
        self.login_url = ''
        self.username = username
        self.password = password
        self.input_text = input_text
        self.page = WebPage('d', chromium_options=self.co)
        self.page.listen.start(self.domain)

    def get_input_ele(self):
        input_elements = self.page.eles('@|tag()=input@|tag()=textarea',timeout=1)
        visible_input_elements = []
        for input_element in input_elements:
            input_type = input_element.attr('type')
            if input_element.states.is_enabled and input_element.states.is_displayed and input_type != "checkbox" and input_type != "file":
                visible_input_elements.append(input_element)
        return visible_input_elements

    def get_submit_name(self):
        # 找出所有可点击的按钮元素
        clickable_buttons = []
        # 查找 input 框中 type 为 "submit" 或 "button" 的元素
        input_elements = self.page.eles("@tag()=input",timeout=1)
        buttons_elements = self.page.eles("@tag()=button",timeout=1)
        for input_element in input_elements:
            input_type = input_element.attr("type")
            if input_type in ["button"]:
                clickable_buttons.append(input_element)
            if input_type in ["submit"]:
                clickable_buttons.append(input_element)
        for button_element in buttons_elements:
            input_type = button_element.attr("type")
            if input_type in ["submit"]:
                clickable_buttons.append(button_element)
        if clickable_buttons == []:
            # 查找直接使用 <button> 标签的元素
            button_elements = self.page.eles("@tag()=button",timeout=1)
            clickable_buttons.extend(button_elements)
        return clickable_buttons

    # def get_login_url(self):
    #     self.page.get(self.target_url)
    #     if "login" in self.page.url:
    #         self.login_url = self.page.url
    #     else:
    #         login_ele = self.page.ele('login')
    #         login_ele.click().wait(0.2)
    #         self.login_url = self.page.url

    def autologin(self):
        # self.get_login_url()
        self.login_url = self.target_url
        self.page.get(self.login_url)
        while True:
            visible_input_elements = self.get_input_ele()
            # username and password
            username_input = visible_input_elements[0]
            password_input = visible_input_elements[1]
            username_input.clear()
            password_input.clear()
            username_input.input(self.username)
            password_input.input(self.password)
            login_buttons = self.get_submit_name()
            if self.username != "admin":
                if len(login_buttons) >= 2:
                    login_button = login_buttons[1]
                    login_button.click().wait(1)
            login_button = login_buttons[0]
            login_button.click().wait(1)
            if self.login_url == self.page.url:
                print("fail login")
            else:
                print("success login")
                break

    def get_route(self):
        # 获取所有的 input 元素
        route_elements = self.page.eles("@tag()=a")
        # 遍历 input 元素,找出 type 不为 hidden 的
        visible_route_urls = []
        for route_element in route_elements:
            route_url = route_element.attr("href")
            visible_route_urls.append(route_url)
        return visible_route_urls

    def autoclick(self):
        routes = self.get_route()
        # self.headers = self.page.session.headers
        for route in routes:
            if "logout" in route:
                self.page.get(route)
                continue
            if "note" in route:
                self.page.get(route)
                self.handle_button(timeo=10)
                self.page.back(1)
                continue
            self.old_url = self.page.url
            self.page.get(route)
            if self.page.url == self.old_url:
                continue
            self.handle_button()
            self.page.back(1)

    def test_click(self):
        routes = self.get_route()

        # self.headers = self.page.session.headers
        for route in routes:
            if "note" in route:
                self.page.get(route)
                buttons_elements = self.page.eles("@tag()=button")
                input_elements = self.get_input_ele()
                selected_input_elements = self.page.eles("@tag()=select", timeout=1)
                if input_elements:
                    for input_element in input_elements:
                        input_element.click()
                        input_element.input(self.input_text)
                if selected_input_elements:
                    for selected_input_element in selected_input_elements:
                        selected_input_element.select.by_index(3)
                buttons_elements[0].click().wait(10)
                self.page.back(1)
            if "passphrasegen" in route:
                self.page.get(route)
                self.handle_button()
                self.page.back(1)

    def generate_random_string(self,length):
        # 包含所有ASCII字母和数字的字符串
        characters = string.ascii_letters + string.digits
        # 随机选择字符
        random_string = ''.join(random.choice(characters) for i in range(length))
        return random_string

    def handle_input(self):
        input_elements = self.get_input_ele()
        selected_input_elements = self.page.eles("@tag()=select",timeout=1)
        if input_elements:
            for input_element in input_elements:
                input_element.click()
                if input_element.attr("name") == "name":
                    input_element.input(self.generate_random_string(10))
                input_element.input(self.input_text)
        if selected_input_elements:
            for selected_input_element in selected_input_elements:
                selected_input_element.select.by_index(1)


    def handle_button(self,timeo=None):
        if timeo:
            buttons_elements = self.page.eles("@tag()=button")
            self.handle_input()
            buttons_elements[0].click().wait(10)
        else:
            buttons_elements = self.page.eles("@tag()=button",timeout=2)
            input_file = self.page.ele("@@tag()=input@@type=file",timeout=2)
            for buttons_element in buttons_elements:
                self.handle_input()
                if "upload" in buttons_element.text.lower():
                    input_file.click.to_upload(f'{self.username}.xml')
                buttons_element.click()

    def get_request_packets(self):
        matched_packets = []
        for packet in self.page.listen.wait(count=99999999, fit_count=False, timeout=3):
            if packet.url.endswith('.js') or packet.url.endswith('.css') or packet.url.endswith(
                    '.ico') or packet.url.endswith('.png') or packet.url.endswith('.jpg') or packet.url.endswith('.jpeg') or packet.url.endswith('.gif') or packet.url.endswith('.txt') or packet.url.endswith('.json'):
                continue
            if tldextract.extract(packet.url).domain != self.domain:
                continue
            matched_packets.append(packet)
        return matched_packets
