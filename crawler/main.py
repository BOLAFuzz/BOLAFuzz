# -*-coding:utf-8 -*-
from DrissionPage import ChromiumPage
import yaml


def load_website_config(file_path):
    """加载网站配置信息"""
    with open(file_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config


def simulate_login(website_config):
    """使用DrissionPage模拟登录"""
    page = ChromiumPage()

    try:
        for site in website_config['websites']:
            print(f"[+] 正在访问 {site['name']} 网站...")
            page.get(site['url'])

            # 假设登录表单的用户名和密码输入框的选择器分别为 '#username' 和 '#password'
            # 登录按钮的选择器为 '#login-button'
            username_input = page.ele('#username')
            password_input = page.ele('#password')
            login_button = page.ele('#login-button')

            if username_input and password_input and login_button:
                username_input.input(site['login']['username'])
                password_input.input(site['login']['password'])
                login_button.click()
                print(f"[+] 已成功登录 {site['name']} 网站")
            else:
                print(f"[-] 无法找到登录表单元素，检查选择器是否正确")
    finally:
        page.quit()

if __name__ == '__main__':
    website_config = load_website_config('config/websites.yaml')
    print(f"[+] Loaded website configuration...")
    simulate_login(website_config)
